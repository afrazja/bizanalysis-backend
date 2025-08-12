from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
import os

from .config import settings
from .schemas import ProductIn, BCGPoint, SWOTIn, SWOTOut, SnapshotIn, SnapshotOut
from .services.bcg import classify_bcg
from .services.swot import build_swot
from .services.porter import forces_index
from .db import Base, engine, get_db, is_database_available
from .models import AnalysisSnapshot

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
