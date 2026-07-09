import uuid
from datetime import datetime

from sqlalchemy import DateTime, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class QCM(Base):
    __tablename__ = "qcms"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    document_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="draft", index=True, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(60), default="medium", nullable=False)
    source_selection: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    ai_request_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    settings = relationship("QCMSettings", back_populates="qcm", cascade="all, delete-orphan", uselist=False)
    questions = relationship("Question", back_populates="qcm", cascade="all, delete-orphan")
