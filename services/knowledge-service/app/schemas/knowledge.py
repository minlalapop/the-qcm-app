from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class UserContext(BaseModel):
    id: str
    email: str
    role: str


class DocumentPage(BaseModel):
    id: str
    page_number: int
    text_content: str


class IndexDocumentRequest(BaseModel):
    force_reindex: bool = False


class KnowledgeIndexPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    document_id: str
    embedding_model: str
    vector_store_type: str
    vector_store_path: str
    dimension: int
    chunks_count: int
    status: str
    created_at: datetime
    updated_at: datetime


class KnowledgeChunkPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    source_page_number: int
    chunk_index: int
    vector_id: int
    content: str
    content_hash: str
    chunk_metadata: dict[str, Any]


class RetrieveRequest(BaseModel):
    query: str = Field(min_length=1)
    document_id: str | None = None
    top_k: int = Field(default=5, ge=1, le=20)
    page_numbers: list[int] = Field(default_factory=list)
    chunk_ids: list[str] = Field(default_factory=list)


class RetrievalResult(BaseModel):
    document_id: str
    chunk_id: str
    chunk_index: int
    source_page_number: int
    score: float
    content: str
    metadata: dict[str, Any]


class RetrieveResponse(BaseModel):
    query: str
    top_k: int
    results: list[RetrievalResult]
