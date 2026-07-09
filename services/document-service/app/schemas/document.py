from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class UserContext(BaseModel):
    id: str
    email: str
    role: str


class DocumentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    original_filename: str
    mime_type: str
    file_size: int
    pdf_hash: str
    status: str
    page_count: int
    created_at: datetime
    updated_at: datetime


class DocumentMetadataPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str | None
    author: str | None
    subject: str | None
    creator: str | None
    producer: str | None
    language: str | None
    page_count: int
    raw_metadata: dict[str, Any]


class DocumentPagePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    page_number: int
    text_content: str


class DocumentImagePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    page_number: int
    image_index: int
    file_path: str
    extension: str
    width: int
    height: int


class ExtractionJobPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    error_message: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime


class DocumentDetail(DocumentSummary):
    metadata_record: DocumentMetadataPublic | None
    pages_count: int
    images_count: int
    latest_job: ExtractionJobPublic | None


class DocumentCachePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cache_type: str
    payload: dict[str, Any]
    updated_at: datetime
