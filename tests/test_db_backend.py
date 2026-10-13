"""Tests for database backend environment toggle and health check endpoint."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.core.config import Settings, settings


@pytest.mark.asyncio
async def test_health_check_returns_db_backend(client: AsyncClient):
    """AC-7: Verify /health returns status and active db_backend."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["db_backend"] == settings.DB_BACKEND


def test_sqlite_backend_resolution():
    """AC-1, AC-2: Verify sqlite backend resolves to aiosqlite and sync sqlite."""
    s = Settings(
        DB_BACKEND="sqlite",
        SQLITE_DATABASE_URL="sqlite+aiosqlite:///./test_custom.db",
        SQLITE_SYNC_DATABASE_URL="sqlite:///./test_custom.db",
    )
    assert s.DB_BACKEND == "sqlite"
    assert s.DATABASE_URL == "sqlite+aiosqlite:///./test_custom.db"
    assert s.SYNC_DATABASE_URL == "sqlite:///./test_custom.db"


def test_neon_backend_resolution():
    """AC-1, AC-3: Verify neon backend resolves to neon connection strings."""
    neon_async = "postgresql+asyncpg://user:pass@ep-host.neon.tech/neondb?ssl=require"
    neon_sync = "postgresql://user:pass@ep-host.neon.tech/neondb?sslmode=require"
    s = Settings(
        DB_BACKEND="neon",
        NEON_DATABASE_URL=neon_async,
        NEON_SYNC_DATABASE_URL=neon_sync,
    )
    assert s.DB_BACKEND == "neon"
    assert s.DATABASE_URL == neon_async
    assert s.SYNC_DATABASE_URL == neon_sync


def test_postgres_backend_resolution():
    """AC-1, AC-3: Verify postgres backend resolves to postgres connection strings."""
    pg_async = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"
    pg_sync = "postgresql://postgres:postgres@localhost:5432/test_db"
    s = Settings(
        DB_BACKEND="postgres",
        POSTGRES_DATABASE_URL=pg_async,
        POSTGRES_SYNC_DATABASE_URL=pg_sync,
    )
    assert s.DB_BACKEND == "postgres"
    assert s.DATABASE_URL == pg_async
    assert s.SYNC_DATABASE_URL == pg_sync
