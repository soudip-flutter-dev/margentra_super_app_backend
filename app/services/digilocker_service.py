"""DigiLocker service — document upload and expiry alert generation."""

from __future__ import annotations

from datetime import date, datetime, timezone

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.digilocker import Document
from app.models.user import User
from app.services.storage_service import upload_file


async def list_documents(
    db: AsyncSession, user: User, offset: int = 0, limit: int = 20
) -> tuple[list[Document], int]:
    from sqlalchemy import desc  # noqa: PLC0415

    count_res = await db.execute(
        select(func.count(Document.id))
        .select_from(Document)
        .where(Document.user_id == user.id)
    )
    total = count_res.scalar_one()
    result = await db.execute(
        select(Document)
        .where(Document.user_id == user.id)
        .order_by(desc(Document.created_at))
        .offset(offset)
        .limit(limit)
    )
    return list(result.scalars().all()), total


async def upload_document(
    db: AsyncSession,
    user: User,
    doc_type: str,
    doc_number: str | None,
    expiry_date: date | None,
    issued_by: str | None,
    issuing_state: str | None,
    file: UploadFile,
) -> Document:
    file_bytes = await file.read()
    ext = file.filename.rsplit(".", 1)[-1] if file.filename and "." in file.filename else "pdf"
    url = await upload_file(
        data=file_bytes,
        filename=f"digilocker/{user.id}/{doc_type}_{doc_number or 'doc'}.{ext}",
        content_type=file.content_type or "application/pdf",
    )
    doc = Document(
        user_id=user.id,
        doc_type=doc_type,
        doc_number=doc_number,
        doc_url=url,
        expiry_date=expiry_date,
        issued_by=issued_by,
        issuing_state=issuing_state,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


async def get_expiry_alerts(db: AsyncSession, user: User) -> list[dict]:
    result = await db.execute(
        select(Document).where(Document.user_id == user.id, Document.expiry_date.isnot(None))
    )
    docs = result.scalars().all()
    alerts = []
    today = date.today()
    for doc in docs:
        if not doc.expiry_date:
            continue
        days_remaining = (doc.expiry_date - today).days
        if days_remaining <= doc.alert_days_before:
            if days_remaining <= 7:
                severity = "critical"
            elif days_remaining <= 14:
                severity = "warning"
            else:
                severity = "info"
            alerts.append(
                {
                    "document_id": doc.id,
                    "doc_type": doc.doc_type,
                    "doc_number": doc.doc_number,
                    "expiry_date": doc.expiry_date,
                    "days_remaining": max(0, days_remaining),
                    "severity": severity,
                }
            )
    return sorted(alerts, key=lambda x: x["days_remaining"])
