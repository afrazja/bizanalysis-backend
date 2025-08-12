from pydantic import BaseModel, Field
from typing import List, Literal

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
