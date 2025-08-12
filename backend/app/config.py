from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    APP_NAME: str = "Biz Analysis API"
    CORS_ORIGINS_RAW: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        # Map the environment variable to our internal field
        fields = {
            'CORS_ORIGINS_RAW': {
                'env': 'CORS_ORIGINS'
            }
        }

    def get_cors_origins(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        return [x.strip() for x in self.CORS_ORIGINS_RAW.split(',') if x.strip()]

settings = Settings()
