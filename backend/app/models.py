import uuid
from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import JSON
from .db import Base

class AnalysisSnapshot(Base):
    __tablename__ = "analysis_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    kind: Mapped[str] = mapped_column(String(20), nullable=False)  # 'SWOT','BCG','PESTLE','PORTER','VRIO','ANSOFF'
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)  # Use JSON instead of JSONB for SQLite compatibility
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
