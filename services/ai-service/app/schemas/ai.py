from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


TaskType = Literal["qcm", "summary", "mindmap"]


class UserContext(BaseModel):
    id: str
    email: str
    role: str


class RetrievalResult(BaseModel):
    document_id: str
    chunk_id: str
    chunk_index: int
    source_page_number: int
    score: float
    content: str
    metadata: dict[str, Any]


class AIRequestBase(BaseModel):
    document_id: str
    query: str | None = None
    top_k: int = Field(default=6, ge=1, le=20)
    page_numbers: list[int] = Field(default_factory=list)
    chunk_ids: list[str] = Field(default_factory=list)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    max_tokens: int = Field(default=1800, ge=128, le=8000)
    extra_instructions: str | None = None


class GenerateQCMRequest(AIRequestBase):
    number_of_questions: int = Field(default=5, ge=1, le=30)
    number_of_options: int = Field(default=4, ge=2, le=6)
    difficulty: str = Field(default="medium")


class GenerateSummaryRequest(AIRequestBase):
    style: str = Field(default="structured")
    max_sections: int = Field(default=6, ge=1, le=12)


class GenerateMindMapRequest(AIRequestBase):
    output_format: Literal["mermaid", "json"] = "mermaid"


class LLMMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class LLMGeneration(BaseModel):
    content: str
    model: str
    provider: str
    usage: dict[str, Any] = Field(default_factory=dict)
    raw: dict[str, Any] = Field(default_factory=dict)


class AIResponsePublic(BaseModel):
    request_id: str
    task_type: TaskType
    provider: str
    model: str
    raw_response: str
    parsed_response: dict[str, Any]
    parser_type: str
    context: list[RetrievalResult]


class AIRequestLogPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    document_id: str | None
    provider: str
    model: str
    task_type: str
    status: str
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    created_at: datetime
