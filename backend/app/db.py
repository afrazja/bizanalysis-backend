import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import Optional

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Warning: DATABASE_URL not set. Database features will be disabled.")
    engine = None
    SessionLocal = None
else:
    try:
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
                "connect_timeout": 10,  # Reduced timeout
                "application_name": "bizanalysis-backend"
            }
        )
        SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        print("Database connection configured successfully")
    except Exception as e:
        print(f"Warning: Could not configure database connection: {e}")
        print("Database features will be disabled.")
        engine = None
        SessionLocal = None

class Base(DeclarativeBase):
    pass

# FastAPI dependency
def get_db():
    if SessionLocal is None:
        raise RuntimeError("Database not available. Please check DATABASE_URL configuration.")
    
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
