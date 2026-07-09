import uuid
from datetime import datetime

from sqlalchemy import DateTime, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MindMap(Base):
    __tablename__ = "mindmaps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    document_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    output_format: Mapped[str] = mapped_column(String(40), default="mermaid", nullable=False)
    mermaid_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    json_content: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    source_selection: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    ai_request_ids: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
