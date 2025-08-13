from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
import os
import uuid

from .config import settings
from .schemas import ProductIn, BCGPoint, SWOTIn, SWOTOut, SnapshotIn, SnapshotOut, CompanyIn, CompanyOut, MarketIn, MarketOut, ProductCreate, ProductOut, SuggestSWOTIn, MarketsBulkIn, ProductsBulkIn, MarketsBulkOut, ProductsBulkOut
from .services.bcg import classify_bcg
from .services.swot import build_swot
from .services.porter import forces_index
from .services.ai_suggest import suggest_swot
from .db import Base, engine, get_db, is_database_available
from .models import AnalysisSnapshot, Company, Market, Product

app = FastAPI(title=settings.APP_NAME, version="0.1.0")

# Create tables on startup
@app.on_event("startup")
def on_startup():
    if engine is not None:
        try:
            Base.metadata.create_all(bind=engine)
            print("Database tables created successfully")
        except Exception as e:
            print(f"Warning: Could not create database tables: {e}")
            print("Database endpoints will not work until connection is established")
    else:
        print("Database not configured - skipping table creation")

# Get CORS origins as a list
cors_origins = settings.get_cors_origins()
print(f"Raw CORS_ORIGINS_RAW: {settings.CORS_ORIGINS_RAW}")
print(f"Parsed CORS Origins: {cors_origins}")

# For now, let's ensure all expected origins are included
expected_origins = [
    "http://localhost:5173",
    "https://bizanalysis-frontend.vercel.app",
    "https://bizanalysis-frontend-2ocu2rw0s-afzjavan-7827s-projects.vercel.app"
]

# Use both parsed and expected origins
final_origins = list(set(cors_origins + expected_origins))
print(f"Final CORS Origins: {final_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=final_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/bcg", response_model=List[BCGPoint])
async def bcg(products: List[ProductIn]):
    return classify_bcg(products)

@app.post("/swot", response_model=SWOTOut)
async def swot(swot: SWOTIn):
    return build_swot(swot)

@app.post("/porter")
async def porter(inputs: Dict[str, float]):
    return forces_index(inputs)

@app.post("/snapshots", response_model=SnapshotOut)
async def create_snapshot(body: SnapshotIn, db: Session = Depends(get_db)):
    if not is_database_available():
        raise HTTPException(status_code=503, detail="Database service unavailable")
    
    try:
        row = AnalysisSnapshot(kind=body.kind, payload=body.payload, note=body.note)
        db.add(row)
        db.commit()
        db.refresh(row)
        return SnapshotOut(id=str(row.id), kind=row.kind, payload=row.payload, note=row.note, created_at=row.created_at)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/snapshots", response_model=list[SnapshotOut])
async def list_snapshots(kind: Optional[str] = None, limit: int = 50, db: Session = Depends(get_db)):
    if not is_database_available():
        raise HTTPException(status_code=503, detail="Database service unavailable")
    
    try:
        q = db.query(AnalysisSnapshot).order_by(AnalysisSnapshot.created_at.desc())
        if kind:
            q = q.filter(AnalysisSnapshot.kind == kind)
        rows = q.limit(min(limit, 200)).all()
        return [SnapshotOut(id=str(r.id), kind=r.kind, payload=r.payload, note=r.note, created_at=r.created_at) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/db-status")
async def db_status():
    return {
        "database_available": is_database_available(),
        "database_url_configured": bool(os.getenv("DATABASE_URL")),
        "message": "Database ready" if is_database_available() else "Database not available - check configuration"
    }

# Companies
@app.post("/companies", response_model=CompanyOut)
async def create_company(body: CompanyIn, db: Session = Depends(get_db)):
    row = Company(name=body.name, industry=body.industry, region=body.region)
    db.add(row); db.commit(); db.refresh(row)
    return CompanyOut(id=str(row.id), **body.model_dump())

@app.get("/companies", response_model=list[CompanyOut])
async def list_companies(db: Session = Depends(get_db)):
    rows = db.query(Company).order_by(Company.name.asc()).all()
    return [CompanyOut(id=str(r.id), name=r.name, industry=r.industry, region=r.region) for r in rows]

# Markets
@app.post("/markets", response_model=MarketOut)
async def create_market(body: MarketIn, db: Session = Depends(get_db)):
    row = Market(company_id=body.company_id, name=body.name, growth_rate=body.growth_rate, size=body.size)
    db.add(row); db.commit(); db.refresh(row)
    return MarketOut(id=str(row.id), **body.model_dump())

@app.get("/markets", response_model=list[MarketOut])
async def list_markets(company_id: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Market)
    if company_id:
        q = q.filter(Market.company_id == company_id)
    rows = q.order_by(Market.name.asc()).all()
    return [MarketOut(id=str(r.id), company_id=str(r.company_id) if r.company_id else None, name=r.name, growth_rate=float(r.growth_rate), size=float(r.size) if r.size is not None else None) for r in rows]

# Products
@app.post("/products", response_model=ProductOut)
async def create_product(body: ProductCreate, db: Session = Depends(get_db)):
    row = Product(**body.model_dump())
    db.add(row); db.commit(); db.refresh(row)
    return ProductOut(id=str(row.id), **body.model_dump())

@app.get("/products", response_model=list[ProductOut])
async def list_products(company_id: str | None = None, market_id: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Product)
    if company_id:
        q = q.filter(Product.company_id == company_id)
    if market_id:
        q = q.filter(Product.market_id == market_id)
    rows = q.order_by(Product.name.asc()).all()
    out: list[ProductOut] = []
    for r in rows:
        out.append(ProductOut(
            id=str(r.id),
            company_id=str(r.company_id) if r.company_id else None,
            market_id=str(r.market_id) if r.market_id else None,
            name=r.name,
            market_share=float(r.market_share) if r.market_share is not None else None,
            largest_rival_share=float(r.largest_rival_share) if r.largest_rival_share is not None else None,
            price=float(r.price) if r.price is not None else None,
            revenue=float(r.revenue) if r.revenue is not None else None,
        ))
    return out

# Bulk endpoints
@app.post("/markets/bulk", response_model=MarketsBulkOut)
async def markets_bulk(body: MarketsBulkIn, db: Session = Depends(get_db)):
    if not is_database_available():
        raise HTTPException(status_code=503, detail="Database service unavailable")
    
    out = []
    for m in body.items:
        row = Market(company_id=m.company_id, name=m.name, growth_rate=m.growth_rate, size=m.size)
        db.add(row); db.flush(); db.refresh(row)
        out.append(MarketOut(id=str(row.id), **m.model_dump()))
    db.commit()
    return MarketsBulkOut(items=out)

@app.post("/products/bulk", response_model=ProductsBulkOut)
async def products_bulk(body: ProductsBulkIn, db: Session = Depends(get_db)):
    if not is_database_available():
        raise HTTPException(status_code=503, detail="Database service unavailable")
    
    out = []
    for p in body.items:
        row = Product(**p.model_dump())
        db.add(row); db.flush(); db.refresh(row)
        out.append(ProductOut(id=str(row.id), **p.model_dump()))
    db.commit()
    return ProductsBulkOut(items=out)

@app.get("/snapshots/{sid}", response_model=SnapshotOut)
async def get_snapshot_by_id(sid: str, db: Session = Depends(get_db)):
    if not is_database_available():
        raise HTTPException(status_code=503, detail="Database service unavailable")
    
    try:
        # For SQLite compatibility, we use string IDs
        row = db.query(AnalysisSnapshot).filter(AnalysisSnapshot.id == sid).first()
        if not row:
            raise HTTPException(status_code=404, detail="Snapshot not found")
        return SnapshotOut(id=str(row.id), kind=row.kind, payload=row.payload, note=row.note, created_at=row.created_at)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/ai/suggest-swot", response_model=SWOTOut)
async def ai_suggest_swot(body: SuggestSWOTIn) -> SWOTOut:
    # For now, always use deterministic heuristic suggester (no external calls)
    return suggest_swot(body)
