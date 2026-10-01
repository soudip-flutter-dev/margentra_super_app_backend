from __future__ import annotations

from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────────────────────────
    APP_NAME: str = "MargNetra Super App"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True
    ALLOWED_HOSTS: str = "*"

    # ── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: str = (
        "postgresql+asyncpg://margnetra:margnetra@localhost:5432/margnetra_db"
    )
    SYNC_DATABASE_URL: str = (
        "postgresql://margnetra:margnetra@localhost:5432/margnetra_db"
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_async_db_url(cls, v: str) -> str:
        if isinstance(v, str):
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql+asyncpg://", 1)
            if v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
                return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @field_validator("SYNC_DATABASE_URL", mode="before")
    @classmethod
    def assemble_sync_db_url(cls, v: str) -> str:
        if isinstance(v, str):
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql://", 1)
            if v.startswith("postgresql+asyncpg://"):
                return v.replace("postgresql+asyncpg://", "postgresql://", 1)
        return v

    # ── JWT ──────────────────────────────────────────────────────────────────
    SECRET_KEY: str = "change-me-in-production-at-least-32-chars"
    JWT_SECRET_KEY: str = "change-jwt-secret-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ── S3 / Object Storage ───────────────────────────────────────────────────
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "ap-south-1"
    S3_BUCKET_NAME: str = "margnetra-storage"
    S3_ENDPOINT_URL: str = ""
    USE_LOCAL_STORAGE: bool = True
    LOCAL_STORAGE_PATH: str = "uploads"

    # ── Email ─────────────────────────────────────────────────────────────────
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "noreply@margnetra.in"
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_NAME: str = "MargNetra"

    # ── RTO / Vahan API ───────────────────────────────────────────────────────
    RTO_API_BASE_URL: str = "https://api.vahan.nic.in/v1"
    RTO_API_KEY: str = ""

    # ── DigiLocker ────────────────────────────────────────────────────────────
    DIGILOCKER_CLIENT_ID: str = ""
    DIGILOCKER_CLIENT_SECRET: str = ""

    # ── Rate Limiting ──────────────────────────────────────────────────────────
    RATE_LIMIT_LOGIN: str = "5/minute"
    RATE_LIMIT_FORGOT_PASSWORD: str = "3/minute"
    RATE_LIMIT_SOS: str = "10/minute"

    # ── MGC Wallet ────────────────────────────────────────────────────────────
    MGC_PER_KM_RATE: float = 1.5
    MGC_BONUS_STREAK_DAYS: int = 7
    MGC_STREAK_PROTECTION_COST: float = 50.0


settings = Settings()
