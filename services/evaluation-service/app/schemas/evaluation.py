from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


ValidationStatus = Literal["approved", "rejected", "needs_revision", "needs_review"]
ReportStatus = Literal["open", "resolved", "rejected"]
DifficultyFit = Literal["too_easy", "adapted", "too_hard", "wrong_level"]
DistractorsQuality = Literal["too_easy", "plausible", "confusing", "invalid"]


class UserContext(BaseModel):
    id: str
    email: str
    role: str


class CreateEvaluationRequest(BaseModel):
    rating: int = Field(ge=1, le=5)
    quality_score: float | None = Field(default=None, ge=0, le=1)
    difficulty_score: float | None = Field(default=None, ge=0, le=1)
    hallucination_score: float | None = Field(default=None, ge=0, le=1)
    validation_status: ValidationStatus = "needs_review"
    is_validated_for_learning: bool = False
    comment: str | None = None
    metadata_payload: dict[str, Any] = Field(default_factory=dict)


class EvaluationPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    qcm_id: str
    reviewer_id: str
    reviewer_role: str
    rating: int
    quality_score: float | None
    difficulty_score: float | None
    hallucination_score: float | None
    validation_status: str
    is_validated_for_learning: bool
    comment: str | None
    metadata_payload: dict[str, Any]
    created_at: datetime


class CorrectedAnswerPayload(BaseModel):
    label: str | None = None
    text: str
    is_correct: bool = False


class CreateQuestionFeedbackRequest(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    question_is_correct: bool | None = None
    correct_answer_is_valid: bool | None = None
    distractors_quality: DistractorsQuality | None = None
    distractors_score: float | None = Field(default=None, ge=0, le=1)
    is_ambiguous: bool = False
    difficulty_fit: DifficultyFit | None = None
    difficulty_score: float | None = Field(default=None, ge=0, le=1)
    issue_types: list[str] = Field(default_factory=list)
    comment: str | None = None
    corrected_question_text: str | None = None
    corrected_answers: list[CorrectedAnswerPayload] = Field(default_factory=list)
    is_validated_example: bool = False
    learning_payload: dict[str, Any] = Field(default_factory=dict)


class FeedbackTagPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tag: str


class QuestionFeedbackPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    qcm_id: str
    question_id: str
    reviewer_id: str
    reviewer_role: str
    rating: int | None
    question_is_correct: bool | None
    correct_answer_is_valid: bool | None
    distractors_quality: str | None
    distractors_score: float | None
    is_ambiguous: bool
    difficulty_fit: str | None
    difficulty_score: float | None
    issue_types: list[str]
    comment: str | None
    corrected_question_text: str | None
    corrected_answers: list[dict[str, Any]]
    is_validated_example: bool
    learning_payload: dict[str, Any]
    tags: list[FeedbackTagPublic]
    created_at: datetime


class CreateHallucinationReportRequest(BaseModel):
    question_id: str | None = None
    reason: str
    evidence: str | None = None


class UpdateHallucinationReportRequest(BaseModel):
    status: ReportStatus


class HallucinationReportPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    qcm_id: str
    question_id: str | None
    reviewer_id: str
    reason: str
    evidence: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class QualityMetricPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    qcm_id: str
    feedback_count: int
    review_count: int
    average_rating: float | None
    quality_score: float | None
    difficulty_score: float | None
    hallucination_score: float | None
    incorrect_questions_count: int
    incorrect_answers_count: int
    ambiguous_questions_count: int
    weak_distractors_count: int
    hallucination_reports_count: int
    computed_payload: dict[str, Any]
    created_at: datetime
