import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class QualityMetric(Base):
    __tablename__ = "quality_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    qcm_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    feedback_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    review_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    average_rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    difficulty_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    hallucination_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    incorrect_questions_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    incorrect_answers_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ambiguous_questions_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    weak_distractors_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hallucination_reports_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    computed_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
