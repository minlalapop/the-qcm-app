from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.feedback_example import FeedbackExample
from app.models.learned_rule import LearnedRule
from app.models.learning_analysis import LearningAnalysis
from app.models.prompt_version import PromptVersion
from app.models.teacher_preference import TeacherPreference
from app.schemas.learning import (
    FeedbackExampleCreate,
    LearningAnalysisPublic,
    QualityMetricSource,
    QuestionFeedbackSource,
    SimilarFeedbackResult,
    UserContext,
)
from app.services.analyzer import build_quality_trends, count_feedback_issues, infer_preferences, recommendations_from_issues
from app.services.embedder import embedder
from app.services.vector_store import search_feedback_index, write_feedback_index


def upsert_learned_rule(db: Session, recommendation: dict, teacher_id: str | None = None) -> LearnedRule:
    scope = f"teacher:{teacher_id}" if teacher_id else "global"
    rule = db.query(LearnedRule).filter(LearnedRule.scope == scope, LearnedRule.rule_key == recommendation["rule_key"]).first()
    if rule:
        rule.support_count += recommendation["support_count"]
        rule.confidence = min(1.0, max(rule.confidence, recommendation["confidence"]))
        rule.rule_text = recommendation["rule_text"]
    else:
        rule = LearnedRule(
            scope=scope,
            teacher_id=teacher_id,
            rule_key=recommendation["rule_key"],
            rule_text=recommendation["rule_text"],
            task_type="qcm",
            confidence=recommendation["confidence"],
            support_count=recommendation["support_count"],
            source_issue_types=[recommendation["rule_key"]],
        )
        db.add(rule)
    db.flush()
    return rule


def upsert_teacher_preference(db: Session, teacher_id: str, preference: dict) -> TeacherPreference:
    record = (
        db.query(TeacherPreference)
        .filter(TeacherPreference.teacher_id == teacher_id, TeacherPreference.preference_key == preference["preference_key"])
        .first()
    )
    if record:
        record.evidence_count += preference["evidence_count"]
        record.weight = min(1.0, max(record.weight, preference["weight"]))
        record.preference_text = preference["preference_text"]
    else:
        record = TeacherPreference(
            teacher_id=teacher_id,
            preference_key=preference["preference_key"],
            preference_text=preference["preference_text"],
            task_type="qcm",
            weight=preference["weight"],
            evidence_count=preference["evidence_count"],
            evidence_payload={"source": "feedback_analysis"},
        )
        db.add(record)
    db.flush()
    return record


def create_prompt_version(db: Session, task_type: str, rules: list[LearnedRule], preferences: list[TeacherPreference]) -> PromptVersion:
    latest = db.query(PromptVersion).filter(PromptVersion.task_type == task_type).order_by(PromptVersion.version.desc()).first()
    next_version = 1 if latest is None else latest.version + 1
    if latest:
        latest.is_active = False

    prompt_version = PromptVersion(
        task_type=task_type,
        base_prompt="Base prompt enrichi par Learning Service.",
        learned_rules_injected=[{"key": rule.rule_key, "text": rule.rule_text} for rule in rules],
        teacher_preferences_injected=[
            {"key": preference.preference_key, "text": preference.preference_text} for preference in preferences
        ],
        version=next_version,
        is_active=True,
    )
    db.add(prompt_version)
    db.flush()
    return prompt_version


def create_feedback_example(db: Session, user: UserContext, payload: FeedbackExampleCreate) -> FeedbackExample:
    example = FeedbackExample(
        qcm_id=payload.qcm_id,
        question_id=payload.question_id,
        teacher_id=user.id,
        original_question=payload.original_question,
        corrected_question=payload.corrected_question,
        corrected_answers=payload.corrected_answers,
        correction_comment=payload.correction_comment,
        tags=payload.tags,
        quality_score=payload.quality_score,
        metadata_payload=payload.metadata_payload,
    )
    db.add(example)
    db.commit()
    db.refresh(example)
    rebuild_feedback_vector_index(db)
    return example


def text_for_example(example: FeedbackExample) -> str:
    parts = [
        example.original_question or "",
        example.corrected_question or "",
        example.correction_comment or "",
        " ".join(example.tags or []),
    ]
    for answer in example.corrected_answers or []:
        parts.append(str(answer.get("text", "")))
    return "\n".join(part for part in parts if part).strip()


def rebuild_feedback_vector_index(db: Session) -> None:
    examples = db.query(FeedbackExample).order_by(FeedbackExample.created_at.asc()).all()
    texts = [text_for_example(example) for example in examples]
    texts = [text if text else "empty feedback example" for text in texts]
    if not texts:
        return

    embeddings = embedder.encode(texts)
    write_feedback_index(embeddings)
    for vector_id, example in enumerate(examples):
        example.vector_id = vector_id
        example.is_indexed = True
    db.commit()


def search_similar_examples(db: Session, query: str, top_k: int, teacher_id: str | None = None) -> list[SimilarFeedbackResult]:
    query_embedding = embedder.encode([query])
    search_result = search_feedback_index(query_embedding, top_k * 3 if teacher_id else top_k)
    if search_result is None:
        return []

    scores, vector_ids = search_result
    examples_by_vector_id = {example.vector_id: example for example in db.query(FeedbackExample).all()}
    results: list[SimilarFeedbackResult] = []
    for score, vector_id in zip(scores[0].tolist(), vector_ids[0].tolist(), strict=False):
        example = examples_by_vector_id.get(vector_id)
        if not example:
            continue
        if teacher_id and example.teacher_id != teacher_id:
            continue
        results.append(
            SimilarFeedbackResult(
                example_id=example.id,
                score=float(score),
                qcm_id=example.qcm_id,
                question_id=example.question_id,
                teacher_id=example.teacher_id,
                corrected_question=example.corrected_question,
                correction_comment=example.correction_comment,
                tags=example.tags,
            )
        )
        if len(results) >= top_k:
            break
    return results


def ingest_validated_examples(db: Session, feedbacks: list[QuestionFeedbackSource]) -> list[FeedbackExample]:
    created_examples: list[FeedbackExample] = []
    for feedback in feedbacks:
        if not feedback.is_validated_example:
            continue
        if not feedback.corrected_question_text and not feedback.corrected_answers:
            continue
        exists = (
            db.query(FeedbackExample)
            .filter(FeedbackExample.qcm_id == feedback.qcm_id, FeedbackExample.question_id == feedback.question_id)
            .first()
        )
        if exists:
            continue
        created_examples.append(
            FeedbackExample(
                qcm_id=feedback.qcm_id,
                question_id=feedback.question_id,
                teacher_id=feedback.reviewer_id,
                corrected_question=feedback.corrected_question_text,
                corrected_answers=feedback.corrected_answers,
                correction_comment=feedback.comment,
                tags=[tag.get("tag") for tag in feedback.tags if tag.get("tag")],
                quality_score=feedback.rating / 5 if feedback.rating else None,
                metadata_payload={"source_feedback_id": feedback.id, "learning_payload": feedback.learning_payload},
            )
        )
    if created_examples:
        db.add_all(created_examples)
        db.commit()
        rebuild_feedback_vector_index(db)
    return created_examples


def analyze_feedback(
    db: Session,
    qcm_id: str,
    metrics: QualityMetricSource,
    feedbacks: list[QuestionFeedbackSource],
    teacher_id: str | None = None,
    create_new_prompt_version: bool = True,
    index_validated_examples: bool = True,
) -> LearningAnalysis:
    issue_counts = count_feedback_issues(feedbacks)
    recommendations = recommendations_from_issues(issue_counts, max(1, len(feedbacks)))
    rules = [upsert_learned_rule(db, recommendation, teacher_id=teacher_id) for recommendation in recommendations]

    preferences = []
    if teacher_id:
        preferences = [upsert_teacher_preference(db, teacher_id, preference) for preference in infer_preferences(feedbacks)]

    if create_new_prompt_version and (rules or preferences):
        create_prompt_version(db, "qcm", rules, preferences)

    indexed_examples = ingest_validated_examples(db, feedbacks) if index_validated_examples else []
    analysis = LearningAnalysis(
        qcm_id=qcm_id,
        teacher_id=teacher_id,
        recurrent_issues=dict(issue_counts),
        quality_trends=build_quality_trends(metrics),
        recommendations=recommendations,
        source_payload={
            "feedback_count": len(feedbacks),
            "metrics": metrics.model_dump(),
            "indexed_examples_count": len(indexed_examples),
        },
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


def active_rules(db: Session, task_type: str = "qcm", teacher_id: str | None = None) -> list[LearnedRule]:
    query = db.query(LearnedRule).filter(LearnedRule.task_type == task_type, LearnedRule.is_active.is_(True))
    if teacher_id:
        query = query.filter(LearnedRule.scope.in_(["global", f"teacher:{teacher_id}"]))
    else:
        query = query.filter(LearnedRule.scope == "global")
    return query.order_by(LearnedRule.confidence.desc(), LearnedRule.support_count.desc()).all()


def active_preferences(db: Session, teacher_id: str | None, task_type: str = "qcm") -> list[TeacherPreference]:
    if not teacher_id:
        return []
    return (
        db.query(TeacherPreference)
        .filter(
            TeacherPreference.teacher_id == teacher_id,
            TeacherPreference.task_type == task_type,
            TeacherPreference.is_active.is_(True),
        )
        .order_by(TeacherPreference.weight.desc(), TeacherPreference.evidence_count.desc())
        .all()
    )
