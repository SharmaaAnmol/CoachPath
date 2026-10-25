"""
Centralized Application Configuration for CoachPath.
Reads environment variables with validation and default fallback values.
"""

from functools import lru_cache
from typing import List, Optional, Union
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
    PORT: Optional[int] = None  # PaaS environments (e.g. Render) inject dynamic PORT

    # Security & Tokens (Phase 3 Auth)
    SECRET_KEY: str = "insecure-default-change-in-production-secret-key-32-chars-min"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    COOKIE_SAMESITE: str = "lax"  # "lax" (same-domain/proxy) or "none" (cross-origin)
    COOKIE_SECURE: Optional[bool] = None  # None -> auto-set to True in staging/production

    # CORS Configuration
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [i.strip().rstrip("/") for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return [i.strip().rstrip("/") for i in v if isinstance(i, str) and i.strip()]
        return ["http://localhost:3000"]

    # Database Configuration (PostgreSQL with asyncpg)
    DATABASE_URL: str = (
        "postgresql+asyncpg://coachpath_user:coachpath_password@localhost:5432/coachpath_db"
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_database_url(cls, v: str) -> str:
        if not v:
            return v
        # Normalize standard postgresql:// or postgres:// to postgresql+asyncpg://
        if v.startswith("postgres://"):
            return "postgresql+asyncpg://" + v[len("postgres://"):]
        if v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
            v = "postgresql+asyncpg://" + v[len("postgresql://"):]
        if "sslmode=" in v:
            v = v.replace("sslmode=", "ssl=")
        return v
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    DB_ECHO: bool = False

    # Redis Cache Configuration (Placeholder / Future Phases)
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI Provider Configuration (Phase 4A & Multi-provider support)
    AI_PROVIDER: str = "gemini"  # "gemini" | "groq" | "openai" | "anthropic" | "disabled"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash-lite"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_REASONING_MODEL: str = "gpt-4o"
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-haiku-20240307"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    AI_REQUEST_TIMEOUT: int = 30
    AI_MAX_RETRIES: int = 2
    ONBOARDING_MAX_TURNS: int = 20

    # Resume Storage & Parsing Configuration (Phase 5A & Staging Durable Storage)
    STORAGE_PROVIDER: str = "local"  # "local" | "s3" | "r2"
    UPLOAD_DIR: str = "uploads"
    MAX_RESUME_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
    RESUME_EXTRACTION_TIMEOUT: int = 45
    S3_ENDPOINT_URL: Optional[str] = None  # e.g. https://<account_id>.r2.cloudflarestorage.com
    S3_ACCESS_KEY_ID: str = ""
    S3_SECRET_ACCESS_KEY: str = ""
    S3_BUCKET_NAME: str = "coachpath-resumes-staging"
    S3_REGION_NAME: str = "auto"

    # Job Ingestion & Market Intelligence Configuration (Phase 8A)
    JOB_INGESTION_ENABLED: bool = True
    JOB_API_PROVIDER: str = "seed"  # "seed" | "manual" | "arbeitnow" | "mock"
    JOB_API_KEY: str = ""
    JOB_API_BASE_URL: str = ""
    JOB_INGESTION_BATCH_SIZE: int = 50
    JOB_INGESTION_RATE_LIMIT_PER_MINUTE: int = 30
    JOB_FRESHNESS_DAYS_ACTIVE: int = 30
    JOB_FRESHNESS_DAYS_STALE: int = 60

    @model_validator(mode="after")
    def validate_production_environment(self) -> "Settings":
        if self.PORT is not None:
            object.__setattr__(self, "API_PORT", self.PORT)

        is_deployed = self.ENVIRONMENT in ("production", "staging")
        if self.COOKIE_SECURE is None:
            object.__setattr__(self, "COOKIE_SECURE", is_deployed)
        if self.COOKIE_SAMESITE.lower() == "none":
            # Cross-origin cookies strictly require Secure=True
            object.__setattr__(self, "COOKIE_SECURE", True)

        if self.ENVIRONMENT == "production":
            if self.DEBUG:
                object.__setattr__(self, "DEBUG", False)
            if self.SECRET_KEY.startswith(("insecure-default", "dev-secret-key")):
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
