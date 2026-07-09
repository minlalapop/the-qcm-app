import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.db.base import Base


class QCMSettings(Base):
    __tablename__ = "qcm_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    qcm_id: Mapped[str] = mapped_column(ForeignKey(f"{settings.DB_SCHEMA}.qcms.id"), unique=True, index=True, nullable=False)
    number_of_questions: Mapped[int] = mapped_column(Integer, nullable=False)
    number_of_options: Mapped[int] = mapped_column(Integer, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(60), nullable=False)
    source_selection: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    duplication_check: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    custom_rules: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    qcm = relationship("QCM", back_populates="settings")
