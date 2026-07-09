import uuid
from datetime import datetime

from sqlalchemy import DateTime, JSON, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DocumentCache(Base):
    __tablename__ = "document_cache"
    __table_args__ = (UniqueConstraint("pdf_hash", "cache_type", name="uq_document_cache_hash_type"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pdf_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    cache_type: Mapped[str] = mapped_column(String(60), index=True, nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
