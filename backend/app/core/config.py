"""
Centralized Application Configuration for CoachPath.
Reads environment variables with validation and default fallback values.
"""

from functools import lru_cache
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings and environment configuration."""

    # Project Metadata
    PROJECT_NAME: str = "CoachPath API"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "AI-Powered Career Intelligence Platform Backend API"
    API_V1_PREFIX: str = "/api/v1"

    # Environment & Logging
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "info"

    # Server Host & Port
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Security & Tokens (Placeholders for Phase 3 Auth)
    SECRET_KEY: str = "insecure-default-change-in-production-secret-key-32-chars-min"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS Configuration
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:3000"]

    # Database Configuration (PostgreSQL with asyncpg)
    DATABASE_URL: str = (
        "postgresql+asyncpg://coachpath_user:coachpath_password@localhost:5432/coachpath_db"
    )
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    DB_ECHO: bool = False

    # Redis Cache Configuration (Placeholder / Future Phases)
    REDIS_URL: str = "redis://localhost:6379/0"

    @model_validator(mode="after")
    def validate_production_environment(self) -> "Settings":
        if self.ENVIRONMENT == "production":
            if self.DEBUG:
                object.__setattr__(self, "DEBUG", False)
            if self.SECRET_KEY.startswith("insecure-default"):
                raise ValueError("Insecure default SECRET_KEY cannot be used in production environment.")
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Returns cached application settings instance."""
    return Settings()


settings = get_settings()
