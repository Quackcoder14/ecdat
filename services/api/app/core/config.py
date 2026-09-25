import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional

class Settings(BaseSettings):
    # Use SQLite for local development, PostgreSQL for production
    DATABASE_URL: str = "sqlite:///./ecdat.db"
    REDIS_URL: str = "redis://localhost:6379"
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24
    ARTIFACT_STORAGE_PATH: str = "/tmp/artifacts"
    MAX_ARTIFACT_SIZE: int = 104857600
    SCAN_TIMEOUT_SECONDS: int = 300
    LLM_PROVIDER: str = "mock"
    LLM_MODEL: str = "demo-model"
    LLM_BASE_URL: Optional[str] = None
    LLM_API_KEY: Optional[str] = None
    DEMO_MODE: bool = True
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file = ".env",
        case_sensitive = True
    )

settings = Settings()