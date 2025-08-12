import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import Optional

DATABASE_URL = os.getenv("DATABASE_URL")

# If DATABASE_URL is provided but connection fails, fallback to SQLite
if DATABASE_URL:
    try:
        # Replace psycopg2:// with postgresql+psycopg:// to use the new driver
        if DATABASE_URL.startswith("postgresql://"):
            DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)

        # Test connection with a quick timeout
        test_engine = create_engine(
            DATABASE_URL, 
            pool_pre_ping=True,
            connect_args={
                "connect_timeout": 5,
                "application_name": "bizanalysis-backend-test"
            }
        )
        
        # Try to connect
        with test_engine.connect() as conn:
            conn.execute("SELECT 1")
        
        # If successful, use the PostgreSQL connection
        engine = create_engine(
            DATABASE_URL, 
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args={
                "options": "-c default_transaction_isolation=read_committed",
                "connect_timeout": 10,
                "application_name": "bizanalysis-backend"
            }
        )
        SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        print("Database connection configured successfully (PostgreSQL)")
        
    except Exception as e:
        print(f"Warning: PostgreSQL connection failed: {e}")
        print("Falling back to SQLite for persistence")
        
        # Fallback to SQLite
        engine = create_engine("sqlite:///./snapshots.db", connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        print("Database connection configured successfully (SQLite fallback)")
        
else:
    print("No DATABASE_URL provided. Using SQLite for persistence")
    engine = create_engine("sqlite:///./snapshots.db", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    print("Database connection configured successfully (SQLite)")

class Base(DeclarativeBase):
    pass

# FastAPI dependency
def get_db():
    if SessionLocal is None:
        raise RuntimeError("Database not available. Please check configuration.")
    
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

# Helper function to check if database is available
def is_database_available() -> bool:
    return engine is not None and SessionLocal is not None
