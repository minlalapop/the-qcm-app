import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class KnowledgeIndex(Base):
    __tablename__ = "embedding_indexes"
    __table_args__ = (UniqueConstraint("owner_id", "document_id", name="uq_knowledge_owner_document"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    document_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(255), nullable=False)
    vector_store_type: Mapped[str] = mapped_column(String(50), default="faiss", nullable=False)
    vector_store_path: Mapped[str] = mapped_column(String(700), nullable=False)
    dimension: Mapped[int] = mapped_column(Integer, nullable=False)
    chunks_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="pending", index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    chunks = relationship("KnowledgeChunk", back_populates="index", cascade="all, delete-orphan")
