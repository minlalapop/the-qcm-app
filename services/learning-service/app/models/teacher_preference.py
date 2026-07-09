import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TeacherPreference(Base):
    __tablename__ = "teacher_preferences"
    __table_args__ = (UniqueConstraint("teacher_id", "preference_key", name="uq_teacher_preferences_key"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    teacher_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    preference_key: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    preference_text: Mapped[str] = mapped_column(Text, nullable=False)
    task_type: Mapped[str] = mapped_column(String(80), default="qcm", index=True, nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    evidence_count: Mapped[int] = mapped_column(default=1, nullable=False)
    evidence_payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
