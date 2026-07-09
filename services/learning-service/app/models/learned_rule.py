import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LearnedRule(Base):
    __tablename__ = "learned_rules"
    __table_args__ = (UniqueConstraint("scope", "rule_key", name="uq_learned_rules_scope_key"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scope: Mapped[str] = mapped_column(String(80), default="global", index=True, nullable=False)
    teacher_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    rule_key: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    rule_text: Mapped[str] = mapped_column(Text, nullable=False)
    task_type: Mapped[str] = mapped_column(String(80), default="qcm", index=True, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    support_count: Mapped[int] = mapped_column(default=1, nullable=False)
    source_issue_types: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
