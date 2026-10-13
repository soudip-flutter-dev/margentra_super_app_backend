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


def test_render_postgres_database_url_resolution():
    """Verify that cloud DATABASE_URL provided by Render takes precedence over localhost default."""
    render_url = "postgres://margnetra_user:secret123@ep-sample-render.oregon-postgres.render.com/margnetra_db"
    s = Settings(
        DB_BACKEND="postgres",
        DATABASE_URL=render_url,
        SYNC_DATABASE_URL=render_url,
    )
    assert s.DB_BACKEND == "postgres"
    assert s.DATABASE_URL == render_url.replace("postgres://", "postgresql+asyncpg://")
    assert s.SYNC_DATABASE_URL == render_url.replace("postgres://", "postgresql://")


def test_inferred_postgres_from_database_url():
    """Verify that when DATABASE_URL is provided without DB_BACKEND, postgres is automatically inferred."""
    render_url = "postgresql://user:pass@render-db:5432/db"
    s = Settings(
        DATABASE_URL=render_url,
    )
    assert s.DB_BACKEND == "postgres"
    assert s.DATABASE_URL.startswith("postgresql+asyncpg://")


def test_alembic_upgrade_on_clean_database(tmp_path):
    """Verify that alembic upgrade head succeeds on a fresh database without NoSuchTableError."""
    from alembic import command
    from alembic.config import Config
    import sqlite3

    db_path = tmp_path / "fresh_test.db"
    sync_url = f"sqlite:///{db_path.as_posix()}"
    async_url = f"sqlite+aiosqlite:///{db_path.as_posix()}"

    cfg = Config("alembic.ini")

    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("DB_BACKEND", "sqlite")
        mp.setenv("SQLITE_DATABASE_URL", async_url)
        mp.setenv("SQLITE_SYNC_DATABASE_URL", sync_url)
        from app.core import config
        mp.setattr(config.settings, "DB_BACKEND", "sqlite")
        mp.setattr(config.settings, "DATABASE_URL", async_url)
        mp.setattr(config.settings, "SYNC_DATABASE_URL", sync_url)

        command.upgrade(cfg, "head")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {r[0] for r in cursor.fetchall()}
    assert "refresh_tokens" in tables
    assert "users" in tables

    cursor.execute("PRAGMA table_info(refresh_tokens)")
    cols = {r[1] for r in cursor.fetchall()}
    assert "revoked_at" in cols
    assert "replaced_by_id" in cols
    conn.close()
