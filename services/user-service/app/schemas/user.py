from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserContext(BaseModel):
    id: str
    email: EmailStr
    role: str


class UserProfilePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    auth_user_id: str
    email: EmailStr
    full_name: str | None
    role: str
    specialty: str | None
    phone: str | None
    avatar_url: str | None
    preferences: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class UserProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=255)
    specialty: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=50)
    avatar_url: str | None = Field(default=None, max_length=500)
    preferences: dict[str, Any] | None = None
