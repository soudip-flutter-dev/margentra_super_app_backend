"""DigiLocker endpoints: list documents, upload, expiry alerts."""

from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, File, Form, UploadFile

from app.core.dependencies import CurrentUserDep, DBDep, PaginationDep
from app.schemas.common import PaginatedResponse
from app.schemas.digilocker import DocumentOut, ExpiryAlertOut, UploadDocumentResponse
from app.services import digilocker_service
from app.utils.pagination import paginate

router = APIRouter(prefix="/digilocker", tags=["DigiLocker"])


@router.get("/documents", response_model=PaginatedResponse[DocumentOut])
async def list_documents(current_user: CurrentUserDep, db: DBDep, pagination: PaginationDep):
    docs, total = await digilocker_service.list_documents(
        db, current_user, offset=pagination.offset, limit=pagination.limit
    )
    return paginate(
        items=[DocumentOut.model_validate(d) for d in docs],
        total=total,
        page=pagination.page,
        limit=pagination.limit,
    )


@router.post("/documents/upload", response_model=UploadDocumentResponse, status_code=201)
async def upload_document(
    current_user: CurrentUserDep,
    db: DBDep,
    doc_type: str = Form(...),
    doc_number: Optional[str] = Form(None),
    expiry_date: Optional[date] = Form(None),
    issued_by: Optional[str] = Form(None),
    issuing_state: Optional[str] = Form(None),
    file: UploadFile = File(...),
):
    doc = await digilocker_service.upload_document(
        db, current_user, doc_type, doc_number, expiry_date, issued_by, issuing_state, file
    )
    return UploadDocumentResponse(document_id=doc.id, doc_url=doc.doc_url, message="Document uploaded")


@router.get("/alerts", response_model=list[ExpiryAlertOut])
async def get_expiry_alerts(current_user: CurrentUserDep, db: DBDep):
    return await digilocker_service.get_expiry_alerts(db, current_user)
