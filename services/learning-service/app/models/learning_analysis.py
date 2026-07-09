import uuid
from datetime import datetime

from sqlalchemy import DateTime, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LearningAnalysis(Base):
    __tablename__ = "learning_analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    qcm_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    teacher_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    analysis_type: Mapped[str] = mapped_column(String(80), default="feedback_analysis", index=True, nullable=False)
    recurrent_issues: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    quality_trends: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    recommendations: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    source_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
