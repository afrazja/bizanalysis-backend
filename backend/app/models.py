import uuid
from sqlalchemy import String, DateTime, Text, Float, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
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

class Company(Base):
    __tablename__ = "companies"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    industry: Mapped[str | None] = mapped_column(String(120))
    region: Mapped[str | None] = mapped_column(String(120))

class Market(Base):
    __tablename__ = "markets"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    growth_rate: Mapped[float] = mapped_column(Numeric(6,2), nullable=False)  # percent
    size: Mapped[float | None] = mapped_column(Numeric(18,2))                 # optional

class Product(Base):
    __tablename__ = "products"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    market_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("markets.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    market_share: Mapped[float | None] = mapped_column(Numeric(6,4))          # 0..1
    largest_rival_share: Mapped[float | None] = mapped_column(Numeric(6,4))   # 0..1
    price: Mapped[float | None] = mapped_column(Numeric(12,2))
    revenue: Mapped[float | None] = mapped_column(Numeric(18,2))
