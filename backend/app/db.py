import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL env var is required")

# Replace psycopg2:// with postgresql+psycopg:// to use the new driver
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

# Add connection arguments to force IPv4 and improve reliability
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={
        "options": "-c default_transaction_isolation=read_committed",
        "connect_timeout": 30,
        "application_name": "bizanalysis-backend"
    }
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

# FastAPI dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
