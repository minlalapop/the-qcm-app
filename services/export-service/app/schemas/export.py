from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class UserContext(BaseModel):
    id: str
    email: str
    role: str


class ExportOptions(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    include_answers: bool = True
    include_explanations: bool = True
    include_sources: bool = True


class ExportPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    owner_id: str
    resource_type: str
    resource_id: str
    export_format: str
    title: str
    file_path: str
    mime_type: str
    status: str
    details: dict[str, Any]
    created_at: datetime


class ExportJobPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    export_id: str | None
    owner_id: str
    resource_type: str
    resource_id: str
    export_format: str
    status: str
    error_message: str | None
    started_at: datetime
    finished_at: datetime | None
    created_at: datetime
