from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    APP_NAME: str = "Biz Analysis API"
    CORS_ORIGINS_RAW: str = "http://localhost:5173"

    model_config = {
        "env_file": ".env",
        "env_prefix": "",
        "case_sensitive": False
    }

    def get_cors_origins(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        return [x.strip() for x in self.CORS_ORIGINS_RAW.split(',') if x.strip()]

# Override the field name for environment variable mapping
class Settings(BaseSettings):
    APP_NAME: str = "Biz Analysis API"
    CORS_ORIGINS_RAW: str = "http://localhost:5173"
    AI_ENABLED: bool = False  # flip to True when wiring a provider
    LLM_PROVIDER: str | None = None  # e.g., "openai" or "azure_openai"
    LLM_API_KEY: str | None = None

    model_config = {
        "env_file": ".env"
    }

    def __init__(self, **kwargs):
        # Map CORS_ORIGINS env var to CORS_ORIGINS_RAW field
        if "CORS_ORIGINS" in os.environ:
            kwargs.setdefault("CORS_ORIGINS_RAW", os.environ["CORS_ORIGINS"])
        super().__init__(**kwargs)

    def get_cors_origins(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        return [x.strip() for x in self.CORS_ORIGINS_RAW.split(',') if x.strip()]

settings = Settings()
