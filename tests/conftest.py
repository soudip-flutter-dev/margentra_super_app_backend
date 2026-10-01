"""pytest configuration, async fixtures, and test database setup."""

from __future__ import annotations

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.dependencies import get_db
from app.db.base import Base
import app.models  # noqa: F401
from app.main import app

# Use a separate in-memory SQLite database for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_factory = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope="session")
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(setup_db) -> AsyncGenerator[AsyncSession, None]:
    async with test_session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# Convenience helper to register + login and get an auth header
@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient) -> dict:
    register_payload = {
        "full_name": "Test User",
        "phone": "+919999999999",
        "email": "test@example.com",
        "password": "TestPass123",
        "confirm_password": "TestPass123",
    }
    await client.post("/api/v1/auth/register", json=register_payload)
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"phone": "+919999999999", "password": "TestPass123"},
    )
    tokens = login_resp.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}
