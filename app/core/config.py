from __future__ import annotations

from typing import Literal

from pydantic import field_validator, model_validator
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
    DB_BACKEND: Literal["sqlite", "neon", "postgres"] = "sqlite"

    SQLITE_DATABASE_URL: str = "sqlite+aiosqlite:///./margnetra.db"
    SQLITE_SYNC_DATABASE_URL: str = "sqlite:///./margnetra.db"

    NEON_DATABASE_URL: str = (
        "postgresql+asyncpg://neondb_owner:npg_udC8yD9ZFcPM@ep-twilight-mouse-b3x4mzdj-pooler.c-4.ap-southeast-1.aws.neon.tech/neondb?ssl=require"
    )
    NEON_SYNC_DATABASE_URL: str = (
        "postgresql://neondb_owner:npg_udC8yD9ZFcPM@ep-twilight-mouse-b3x4mzdj-pooler.c-4.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    )

    POSTGRES_DATABASE_URL: str = (
        "postgresql+asyncpg://margnetra:margnetra@localhost:5432/margnetra_db"
    )
    POSTGRES_SYNC_DATABASE_URL: str = (
        "postgresql://margnetra:margnetra@localhost:5432/margnetra_db"
    )

    DATABASE_URL: str = ""
    SYNC_DATABASE_URL: str = ""

    @model_validator(mode="after")
    def resolve_database_urls(self) -> Settings:
        backend = (self.DB_BACKEND or "sqlite").lower()
        if backend == "sqlite":
            async_url = self.SQLITE_DATABASE_URL or "sqlite+aiosqlite:///./margnetra.db"
            sync_url = self.SQLITE_SYNC_DATABASE_URL or "sqlite:///./margnetra.db"
        elif backend == "neon":
            async_url = self.NEON_DATABASE_URL or self.DATABASE_URL
            sync_url = self.NEON_SYNC_DATABASE_URL or self.SYNC_DATABASE_URL
        elif backend == "postgres":
            async_url = self.POSTGRES_DATABASE_URL or self.DATABASE_URL
            sync_url = self.POSTGRES_SYNC_DATABASE_URL or self.SYNC_DATABASE_URL
        else:
            raise ValueError(f"Unsupported DB_BACKEND '{backend}'. Must be sqlite, neon, or postgres.")

        # Ensure correct driver prefixes
        if async_url.startswith("postgres://"):
            async_url = async_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif async_url.startswith("postgresql://") and not async_url.startswith("postgresql+asyncpg://"):
            async_url = async_url.replace("postgresql://", "postgresql+asyncpg://", 1)

        if sync_url.startswith("postgres://"):
            sync_url = sync_url.replace("postgres://", "postgresql://", 1)
        elif sync_url.startswith("postgresql+asyncpg://"):
            sync_url = sync_url.replace("postgresql+asyncpg://", "postgresql://", 1)

        self.DATABASE_URL = async_url
        self.SYNC_DATABASE_URL = sync_url
        return self

    # ── JWT ──────────────────────────────────────────────────────────────────
    SECRET_KEY: str = "change-me-in-production-at-least-32-chars"
    JWT_SECRET_KEY: str = "change-jwt-secret-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    REFRESH_TOKEN_ROTATION_GRACE_SECONDS: int = 30

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
