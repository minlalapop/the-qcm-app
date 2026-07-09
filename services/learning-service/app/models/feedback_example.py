import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FeedbackExample(Base):
    __tablename__ = "feedback_examples"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    qcm_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    question_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    teacher_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    original_question: Mapped[str | None] = mapped_column(Text, nullable=True)
    corrected_question: Mapped[str | None] = mapped_column(Text, nullable=True)
    corrected_answers: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    correction_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    vector_id: Mapped[int | None] = mapped_column(default=None, nullable=True)
    is_indexed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    metadata_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
