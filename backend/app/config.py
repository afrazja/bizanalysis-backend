from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Biz Analysis API"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "https://bizanalysis-frontend.vercel.app",
        "https://bizanalysis-frontend-*.vercel.app"  # Allow preview deployments
    ]

    class Config:
        env_file = ".env"

settings = Settings()
