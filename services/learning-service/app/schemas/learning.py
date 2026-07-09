from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class UserContext(BaseModel):
    id: str
    email: str
    role: str


class QuestionFeedbackSource(BaseModel):
    id: str
    qcm_id: str
    question_id: str
    reviewer_id: str
    reviewer_role: str
    rating: int | None = None
    question_is_correct: bool | None = None
    correct_answer_is_valid: bool | None = None
    distractors_quality: str | None = None
    distractors_score: float | None = None
    is_ambiguous: bool = False
    difficulty_fit: str | None = None
    difficulty_score: float | None = None
    issue_types: list[str] = Field(default_factory=list)
    comment: str | None = None
    corrected_question_text: str | None = None
    corrected_answers: list[dict[str, Any]] = Field(default_factory=list)
    is_validated_example: bool = False
    learning_payload: dict[str, Any] = Field(default_factory=dict)
    tags: list[dict[str, Any]] = Field(default_factory=list)


class QualityMetricSource(BaseModel):
    qcm_id: str
    feedback_count: int
    review_count: int
    average_rating: float | None = None
    quality_score: float | None = None
    difficulty_score: float | None = None
    hallucination_score: float | None = None
    incorrect_questions_count: int
    incorrect_answers_count: int
    ambiguous_questions_count: int
    weak_distractors_count: int
    hallucination_reports_count: int
    computed_payload: dict[str, Any] = Field(default_factory=dict)


class AnalyzeQCMRequest(BaseModel):
    teacher_id: str | None = None
    create_prompt_version: bool = True
    index_validated_examples: bool = True


class LearningAnalysisPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    qcm_id: str
    teacher_id: str | None
    analysis_type: str
    recurrent_issues: dict[str, Any]
    quality_trends: dict[str, Any]
    recommendations: list[Any]
    source_payload: dict[str, Any]
    created_at: datetime


class LearnedRulePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    scope: str
    teacher_id: str | None
    rule_key: str
    rule_text: str
    task_type: str
    confidence: float
    support_count: int
    source_issue_types: list[str]
    is_active: bool


class TeacherPreferencePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    teacher_id: str
    preference_key: str
    preference_text: str
    task_type: str
    weight: float
    evidence_count: int
    evidence_payload: dict[str, Any]
    is_active: bool


class FeedbackExampleCreate(BaseModel):
    qcm_id: str
    question_id: str
    original_question: str | None = None
    corrected_question: str | None = None
    corrected_answers: list[dict[str, Any]] = Field(default_factory=list)
    correction_comment: str | None = None
    tags: list[str] = Field(default_factory=list)
    quality_score: float | None = Field(default=None, ge=0, le=1)
    metadata_payload: dict[str, Any] = Field(default_factory=dict)


class FeedbackExamplePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    qcm_id: str
    question_id: str
    teacher_id: str
    original_question: str | None
    corrected_question: str | None
    corrected_answers: list[dict[str, Any]]
    correction_comment: str | None
    tags: list[str]
    quality_score: float | None
    vector_id: int | None
    is_indexed: bool
    metadata_payload: dict[str, Any]


class SimilarFeedbackRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    teacher_id: str | None = None


class SimilarFeedbackResult(BaseModel):
    example_id: str
    score: float
    qcm_id: str
    question_id: str
    teacher_id: str
    corrected_question: str | None
    correction_comment: str | None
    tags: list[str]


class PromptContextResponse(BaseModel):
    task_type: str
    teacher_id: str | None
    learned_rules: list[LearnedRulePublic]
    teacher_preferences: list[TeacherPreferencePublic]
    similar_examples: list[SimilarFeedbackResult]
