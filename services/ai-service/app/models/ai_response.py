import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.db.base import Base


class AIResponse(Base):
    __tablename__ = "ai_responses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id: Mapped[str] = mapped_column(ForeignKey(f"{settings.DB_SCHEMA}.ai_requests.id"), unique=True, index=True, nullable=False)
    raw_response: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_response: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    parser_type: Mapped[str] = mapped_column(String(60), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    request = relationship("AIRequest", back_populates="response")
