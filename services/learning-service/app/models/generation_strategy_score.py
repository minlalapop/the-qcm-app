import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class GenerationStrategyScore(Base):
    __tablename__ = "strategy_scores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    strategy_key: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    task_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    average_rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    hallucination_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    support_count: Mapped[int] = mapped_column(default=0, nullable=False)
    evidence_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
