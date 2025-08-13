from pydantic import BaseModel, Field
from typing import List, Literal, Any, Dict, Optional
from datetime import datetime

class ProductIn(BaseModel):
    name: str = Field(..., examples=["Product A"])
    market_share: float = Field(..., ge=0, le=1, description="0..1")
    largest_rival_share: float = Field(..., ge=0, le=1, description="0..1")
    market_growth_rate: float = Field(..., description="% e.g., 12 for 12%")

class BCGPoint(BaseModel):
    name: str
    rms: float
    growth: float
    quadrant: Literal["Star", "Cash Cow", "Question Mark", "Dog"]

class SWOTIn(BaseModel):
    strengths: List[str] = []
    weaknesses: List[str] = []
    opportunities: List[str] = []
    threats: List[str] = []

class SWOTOut(SWOTIn):
    pass

class SnapshotIn(BaseModel):
    kind: Literal["SWOT","BCG","PESTLE","PORTER","VRIO","ANSOFF"]
    payload: Dict[str, Any]
    note: Optional[str] = None

class SnapshotOut(SnapshotIn):
    id: str
    created_at: datetime

class CompanyIn(BaseModel):
    name: str
    industry: Optional[str] = None
    region: Optional[str] = None

class CompanyOut(CompanyIn):
    id: str

class MarketIn(BaseModel):
    company_id: Optional[str] = None
    name: str
    growth_rate: float  # percent
    size: Optional[float] = None

class MarketOut(MarketIn):
    id: str

class ProductCreate(BaseModel):
    company_id: Optional[str] = None
    market_id: Optional[str] = None
    name: str
    market_share: Optional[float] = None  # 0..1
    largest_rival_share: Optional[float] = None  # 0..1
    price: Optional[float] = None
    revenue: Optional[float] = None

class ProductOut(ProductCreate):
    id: str

class MarketCtx(BaseModel):
    name: str
    growth_rate: float  # percent

class ProductCtx(BaseModel):
    name: str
    market_share: float  # 0..1
    largest_rival_share: float  # 0..1

class SuggestSWOTIn(BaseModel):
    company: Optional[str] = None
    industry: Optional[str] = None
    markets: List[MarketCtx] = []
    products: List[ProductCtx] = []
    # optional: pass computed BCG points directly
    points: Optional[List[BCGPoint]] = None

class MarketsBulkIn(BaseModel):
    items: List[MarketIn]

class ProductsBulkIn(BaseModel):
    items: List[ProductCreate]

class MarketsBulkOut(BaseModel):
    items: List[MarketOut]

class ProductsBulkOut(BaseModel):
    items: List[ProductOut]
