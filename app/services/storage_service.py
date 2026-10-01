"""Storage service — abstraction over local disk or S3-compatible object storage."""

from __future__ import annotations

import os
from pathlib import Path

from app.core.config import settings


async def upload_file(data: bytes, filename: str, content_type: str = "application/octet-stream") -> str:
    """Upload bytes and return the public URL."""
    if settings.USE_LOCAL_STORAGE:
        return await _upload_local(data, filename)
    return await _upload_s3(data, filename, content_type)


async def _upload_local(data: bytes, filename: str) -> str:
    base = Path(settings.LOCAL_STORAGE_PATH)
    target = base / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    # In a real dev setup, serve from /uploads via StaticFiles
    return f"/uploads/{filename}"


async def _upload_s3(data: bytes, filename: str, content_type: str) -> str:
    import aiobotocore.session  # noqa: PLC0415

    session = aiobotocore.session.get_session()
    kwargs: dict = {
        "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
        "region_name": settings.AWS_REGION,
    }
    if settings.S3_ENDPOINT_URL:
        kwargs["endpoint_url"] = settings.S3_ENDPOINT_URL

    async with session.create_client("s3", **kwargs) as client:
        await client.put_object(
            Bucket=settings.S3_BUCKET_NAME,
            Key=filename,
            Body=data,
            ContentType=content_type,
            ACL="public-read",
        )

    endpoint = settings.S3_ENDPOINT_URL or f"https://s3.{settings.AWS_REGION}.amazonaws.com"
    return f"{endpoint}/{settings.S3_BUCKET_NAME}/{filename}"
