from statistics import mean

from sqlalchemy.orm import Session

from app.models.evaluation import Evaluation
from app.models.hallucination_report import HallucinationReport
from app.models.quality_metric import QualityMetric
from app.models.question_feedback import QuestionFeedback


def average(values: list[float | int | None]) -> float | None:
    cleaned_values = [float(value) for value in values if value is not None]
    return round(mean(cleaned_values), 4) if cleaned_values else None


def compute_quality_metrics(db: Session, qcm_id: str) -> QualityMetric:
    reviews = db.query(Evaluation).filter(Evaluation.qcm_id == qcm_id).all()
    feedbacks = db.query(QuestionFeedback).filter(QuestionFeedback.qcm_id == qcm_id).all()
    hallucinations = db.query(HallucinationReport).filter(HallucinationReport.qcm_id == qcm_id).all()

    incorrect_questions_count = sum(1 for feedback in feedbacks if feedback.question_is_correct is False)
    incorrect_answers_count = sum(1 for feedback in feedbacks if feedback.correct_answer_is_valid is False)
    ambiguous_questions_count = sum(1 for feedback in feedbacks if feedback.is_ambiguous)
    weak_distractors_count = sum(1 for feedback in feedbacks if feedback.distractors_quality == "too_easy")
    open_hallucinations_count = sum(1 for report in hallucinations if report.status == "open")

    metric = QualityMetric(
        qcm_id=qcm_id,
        feedback_count=len(feedbacks),
        review_count=len(reviews),
        average_rating=average([review.rating for review in reviews] + [feedback.rating for feedback in feedbacks]),
        quality_score=average([review.quality_score for review in reviews]),
        difficulty_score=average(
            [review.difficulty_score for review in reviews] + [feedback.difficulty_score for feedback in feedbacks]
        ),
        hallucination_score=average([review.hallucination_score for review in reviews]),
        incorrect_questions_count=incorrect_questions_count,
        incorrect_answers_count=incorrect_answers_count,
        ambiguous_questions_count=ambiguous_questions_count,
        weak_distractors_count=weak_distractors_count,
        hallucination_reports_count=open_hallucinations_count,
        computed_payload={
            "learning_ready_examples": sum(1 for feedback in feedbacks if feedback.is_validated_example),
            "issue_type_counts": count_issue_types(feedbacks),
            "open_hallucination_reports": open_hallucinations_count,
        },
    )
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric


def count_issue_types(feedbacks: list[QuestionFeedback]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for feedback in feedbacks:
        for issue_type in feedback.issue_types:
            counts[issue_type] = counts.get(issue_type, 0) + 1
    return counts
