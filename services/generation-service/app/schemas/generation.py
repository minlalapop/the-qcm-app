from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class UserContext(BaseModel):
    id: str
    email: str
    role: str


class SourceSelection(BaseModel):
    document_ids: list[str] = Field(min_length=1)
    page_numbers: list[int] = Field(default_factory=list)
    chunk_ids: list[str] = Field(default_factory=list)
    focus_text: str | None = None


class GenerateQCMRequest(BaseModel):
    title: str = Field(default="Nouveau QCM", max_length=255)
    source_selection: SourceSelection
    number_of_questions: int = Field(default=5, ge=1, le=60)
    number_of_options: int = Field(default=4, ge=2, le=6)
    difficulty: str = Field(default="medium", max_length=60)
    top_k: int = Field(default=6, ge=1, le=20)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    max_tokens: int = Field(default=1800, ge=128, le=8000)
    duplication_check: bool = True
    custom_rules: dict[str, Any] = Field(default_factory=dict)


class GenerateSummaryRequest(BaseModel):
    title: str = Field(default="Resume", max_length=255)
    source_selection: SourceSelection
    style: str = Field(default="concise_structured", max_length=80)
    max_sections: int = Field(default=6, ge=1, le=10)
    top_k: int = Field(default=5, ge=1, le=15)
    temperature: float = Field(default=0.15, ge=0.0, le=2.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    max_tokens: int = Field(default=1200, ge=128, le=4000)
    custom_rules: dict[str, Any] = Field(default_factory=dict)


class GenerateMindMapRequest(BaseModel):
    title: str = Field(default="MindMap", max_length=255)
    source_selection: SourceSelection
    output_format: Literal["mermaid", "json"] = "mermaid"
    top_k: int = Field(default=6, ge=1, le=20)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    max_tokens: int = Field(default=1800, ge=128, le=6000)
    custom_rules: dict[str, Any] = Field(default_factory=dict)


class AnswerPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    label: str
    answer_text: str
    is_correct: bool
    is_distractor: bool
    order_index: int


class AnswerUpdate(BaseModel):
    label: str | None = Field(default=None, max_length=10)
    answer_text: str | None = None
    is_correct: bool | None = None
    order_index: int | None = None


class QuestionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    order_index: int
    question_text: str
    explanation: str | None
    difficulty: str | None
    source_document_id: str | None
    source_page: int | None
    source_chunk_id: str | None
    citation: str | None
    answers: list[AnswerPublic]


class QuestionUpdate(BaseModel):
    question_text: str | None = None
    explanation: str | None = None
    difficulty: str | None = Field(default=None, max_length=60)
    source_page: int | None = None
    source_chunk_id: str | None = None
    citation: str | None = None
    answers: list[AnswerUpdate] | None = None


class QCMSettingsPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    number_of_questions: int
    number_of_options: int
    difficulty: str
    source_selection: dict[str, Any]
    duplication_check: bool
    custom_rules: dict[str, Any]


class QCMPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    title: str
    document_ids: list[str]
    status: str
    difficulty: str
    source_selection: dict[str, Any]
    ai_request_ids: list[str]
    settings: QCMSettingsPublic | None
    questions: list[QuestionPublic]
    created_at: datetime
    updated_at: datetime


class QCMUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    status: str | None = Field(default=None, max_length=40)
    difficulty: str | None = Field(default=None, max_length=60)


class SummaryPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    title: str
    document_ids: list[str]
    content: str
    structured_payload: dict[str, Any]
    source_selection: dict[str, Any]
    ai_request_ids: list[str]
    created_at: datetime


class SummaryUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)


class MindMapPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    title: str
    document_ids: list[str]
    output_format: str
    mermaid_content: str | None
    json_content: dict[str, Any]
    source_selection: dict[str, Any]
    ai_request_ids: list[str]
    created_at: datetime


class MindMapUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
