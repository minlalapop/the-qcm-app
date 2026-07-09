from sqlalchemy.orm import Session

from app.models.evaluation import Evaluation
from app.models.feedback_tag import FeedbackTag
from app.models.hallucination_report import HallucinationReport
from app.models.question_feedback import QuestionFeedback
from app.schemas.evaluation import (
    CreateEvaluationRequest,
    CreateHallucinationReportRequest,
    CreateQuestionFeedbackRequest,
    UpdateHallucinationReportRequest,
    UserContext,
)
from app.services.metrics import compute_quality_metrics


def create_evaluation(db: Session, qcm_id: str, user: UserContext, payload: CreateEvaluationRequest) -> Evaluation:
    evaluation = Evaluation(
        qcm_id=qcm_id,
        reviewer_id=user.id,
        reviewer_role=user.role,
        **payload.model_dump(),
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)
    compute_quality_metrics(db, qcm_id)
    return evaluation


def create_question_feedback(
    db: Session,
    qcm_id: str,
    question_id: str,
    user: UserContext,
    payload: CreateQuestionFeedbackRequest,
) -> QuestionFeedback:
    payload_data = payload.model_dump()
    corrected_answers = [answer.model_dump() for answer in payload.corrected_answers]
    payload_data["corrected_answers"] = corrected_answers

    feedback = QuestionFeedback(
        qcm_id=qcm_id,
        question_id=question_id,
        reviewer_id=user.id,
        reviewer_role=user.role,
        **payload_data,
    )
    db.add(feedback)
    db.flush()

    for tag in build_feedback_tags(payload):
        db.add(FeedbackTag(feedback_id=feedback.id, tag=tag))

    db.commit()
    db.refresh(feedback)
    compute_quality_metrics(db, qcm_id)
    return feedback


def build_feedback_tags(payload: CreateQuestionFeedbackRequest) -> list[str]:
    tags = set(payload.issue_types)
    if payload.question_is_correct is False:
        tags.add("question_incorrecte")
    if payload.correct_answer_is_valid is False:
        tags.add("reponse_incorrecte")
    if payload.distractors_quality == "too_easy":
        tags.add("distracteurs_trop_faciles")
    if payload.is_ambiguous:
        tags.add("question_ambigue")
    if payload.difficulty_fit in {"too_easy", "too_hard", "wrong_level"}:
        tags.add("difficulte_mal_adaptee")
    if payload.corrected_question_text or payload.corrected_answers:
        tags.add("correction_enseignant")
    if payload.is_validated_example:
        tags.add("exemple_valide_learning")
    return sorted(tags)


def create_hallucination_report(
    db: Session,
    qcm_id: str,
    user: UserContext,
    payload: CreateHallucinationReportRequest,
) -> HallucinationReport:
    report = HallucinationReport(
        qcm_id=qcm_id,
        question_id=payload.question_id,
        reviewer_id=user.id,
        reason=payload.reason,
        evidence=payload.evidence,
        status="open",
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    compute_quality_metrics(db, qcm_id)
    return report


def update_hallucination_report(
    db: Session,
    report: HallucinationReport,
    payload: UpdateHallucinationReportRequest,
) -> HallucinationReport:
    report.status = payload.status
    db.commit()
    db.refresh(report)
    compute_quality_metrics(db, report.qcm_id)
    return report
