"""Pagination helper — build PaginatedResponse from a list + total."""

from __future__ import annotations

import math
from typing import Generic, TypeVar

from app.schemas.common import PaginatedResponse

T = TypeVar("T")


def paginate(items: list, total: int, page: int, limit: int) -> dict:
    pages = math.ceil(total / limit) if limit else 1
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
    }
