"""Application configuration management.

All settings are loaded from environment variables (`.env`) using
`pydantic-settings`. No hardcoded values are allowed outside this module.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings loaded from environment / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "Career Intelligence Platform"
    app_version: str = "1.0.0"
    environment: Literal["development", "staging", "production", "test"] = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # Security
    secret_key: str = "dev-insecure-secret-change-me"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30
    algorithm: str = "HS256"
    backend_cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    # Database
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "career"
    postgres_password: str = "career"
    postgres_db: str = "career_intelligence"
    database_url: str | None = None

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_url: str | None = None

    # Celery
    celery_broker_url: str | None = None
    celery_result_backend: str | None = None

    # MLflow
    mlflow_tracking_uri: str = "http://localhost:5000"
    mlflow_model_registry_name: str = "salary-predictor"
    mlflow_experiment_name: str = "salary-prediction"
    ml_model_path: str = "ml/models/trained"

    # Storage
    storage_backend: Literal["local", "s3"] = "local"
    storage_local_path: str = "storage"
    s3_bucket: str | None = None
    s3_region: str | None = None
    s3_access_key: str | None = None
    s3_secret_key: str | None = None

    # NLP
    spacy_model: str = "en_core_web_lg"
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384

    # Rate limiting
    rate_limit_default: str = "100/minute"
    rate_limit_auth: str = "10/minute"

    # Model defaults
    salary_default_confidence: float = 0.9

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def _parse_cors(cls, value: object) -> object:
        """Accept a JSON-array string for CORS origins."""
        if isinstance(value, str) and value.startswith("["):
            import json

            return json.loads(value)
        return value

    @property
    def sqlalchemy_database_uri(self) -> str:
        """Resolve the SQLAlchemy database URI."""
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def resolved_redis_url(self) -> str:
        """Resolve the Redis URL."""
        if self.redis_url:
            return self.redis_url
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    @property
    def resolved_celery_broker_url(self) -> str:
        """Resolve the Celery broker URL."""
        if self.celery_broker_url:
            return self.celery_broker_url
        return self.resolved_redis_url.replace("/0", "/1")

    @property
    def resolved_celery_result_backend(self) -> str:
        """Resolve the Celery result backend URL."""
        if self.celery_result_backend:
            return self.celery_result_backend
        return self.resolved_redis_url.replace("/0", "/2")


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton instance of the application settings."""
    return Settings()


settings = get_settings()
