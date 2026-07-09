from app.schemas.learning import QuestionFeedbackSource
from app.services.analyzer import count_feedback_issues


def test_count_feedback_issues_detects_ambiguity() -> None:
    feedback = QuestionFeedbackSource(
        id="f1",
        qcm_id="qcm1",
        question_id="q1",
        reviewer_id="teacher1",
        reviewer_role="teacher",
        is_ambiguous=True,
    )

    counts = count_feedback_issues([feedback])

    assert counts["question_ambigue"] == 1
