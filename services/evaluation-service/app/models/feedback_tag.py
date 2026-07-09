import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.db.base import Base


class FeedbackTag(Base):
    __tablename__ = "feedback_tags"
    __table_args__ = (UniqueConstraint("feedback_id", "tag", name="uq_feedback_tags_feedback_tag"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    feedback_id: Mapped[str] = mapped_column(
        ForeignKey(f"{settings.DB_SCHEMA}.question_feedback.id"),
        index=True,
        nullable=False,
    )
    tag: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    feedback = relationship("QuestionFeedback", back_populates="tags")
