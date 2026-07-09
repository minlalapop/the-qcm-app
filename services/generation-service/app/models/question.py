import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.db.base import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    qcm_id: Mapped[str] = mapped_column(ForeignKey(f"{settings.DB_SCHEMA}.qcms.id"), index=True, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    difficulty: Mapped[str | None] = mapped_column(String(60), nullable=True)
    source_document_id: Mapped[str | None] = mapped_column(String(36), index=True, nullable=True)
    source_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_chunk_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    citation: Mapped[str | None] = mapped_column(Text, nullable=True)
    question_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    qcm = relationship("QCM", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
