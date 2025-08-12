from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    APP_NAME: str = "Biz Analysis API"
    CORS_ORIGINS_RAW: str = "http://localhost:5173"

    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        return [x.strip() for x in self.CORS_ORIGINS_RAW.split(',') if x.strip()]

    class Config:
        env_file = ".env"
        # Map the environment variable to our internal field
        fields = {
            'CORS_ORIGINS_RAW': {
                'env': 'CORS_ORIGINS'
            }
        }

settings = Settings()
