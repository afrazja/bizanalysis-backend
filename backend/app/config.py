from pydantic_settings import BaseSettings
from typing import List
import os

def _split_env(name: str, default: List[str]) -> List[str]:
    """Split comma-separated environment variable into list of strings."""
    raw = os.getenv(name)
    if not raw:
        return default
    return [x.strip() for x in raw.split(',') if x.strip()]

class Settings(BaseSettings):
    APP_NAME: str = "Biz Analysis API"
    CORS_ORIGINS: List[str] = _split_env(
        "CORS_ORIGINS",
        ["http://localhost:5173"]
    )

    class Config:
        env_file = ".env"

settings = Settings()
