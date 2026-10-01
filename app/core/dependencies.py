"""Shared FastAPI dependencies: DB session, current user, pagination, RBAC."""

from __future__ import annotations

from typing import Annotated, AsyncGenerator, TYPE_CHECKING

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_access_token
from app.db.session import async_session_factory

from app.models.user import User

# ── Database session ──────────────────────────────────────────────────────────
bearer_scheme = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ── Auth dependency ───────────────────────────────────────────────────────────
async def get_current_user_payload(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
) -> dict:
    """Validate JWT and return raw payload dict."""
    payload = verify_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    payload: Annotated[dict, Depends(get_current_user_payload)],
) -> User:
    """Resolve the current authenticated user from the DB."""
    from sqlalchemy import select  # noqa: PLC0415

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bad token payload",
        )

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is deactivated",
        )
    return user


# ── Pagination ────────────────────────────────────────────────────────────────
class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number (1-indexed)"),
        limit: int = Query(20, ge=1, le=100, description="Items per page"),
    ):
        self.page = page
        self.limit = limit
        self.offset = (page - 1) * limit


# ── Type aliases ──────────────────────────────────────────────────────────────
DBDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
PaginationDep = Annotated[PaginationParams, Depends(PaginationParams)]
