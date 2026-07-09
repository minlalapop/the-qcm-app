import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class QuestionFeedback(Base):
    __tablename__ = "question_feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    qcm_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    question_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    reviewer_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    reviewer_role: Mapped[str] = mapped_column(String(60), nullable=False)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    question_is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    correct_answer_is_valid: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    distractors_quality: Mapped[str | None] = mapped_column(String(80), nullable=True)
    distractors_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_ambiguous: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    difficulty_fit: Mapped[str | None] = mapped_column(String(80), nullable=True)
    difficulty_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    issue_types: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    corrected_question_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    corrected_answers: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    is_validated_example: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    learning_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    tags = relationship("FeedbackTag", back_populates="feedback", cascade="all, delete-orphan")
