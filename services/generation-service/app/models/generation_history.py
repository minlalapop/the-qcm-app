import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class GenerationHistory(Base):
    __tablename__ = "generation_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    resource_type: Mapped[str] = mapped_column(String(60), index=True, nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    document_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    ai_request_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    model: Mapped[str | None] = mapped_column(String(255), nullable=True)
    parameters: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    generated_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    average_feedback_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
