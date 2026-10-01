"""Emergency SOS endpoints: trigger, contacts, road assistance."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.dependencies import CurrentUserDep, DBDep
from app.schemas.sos import (
    EmergencyContactOut,
    RoadAssistanceRequest,
    RoadAssistanceResponse,
    TriggerSOSRequest,
    TriggerSOSResponse,
    UpsertContactRequest,
)
from app.services import sos_service

router = APIRouter(prefix="/sos", tags=["SOS"])


@router.post("/trigger", response_model=TriggerSOSResponse, status_code=201)
async def trigger_sos(data: TriggerSOSRequest, current_user: CurrentUserDep, db: DBDep):
    """Trigger an emergency SOS alert to all registered emergency contacts."""
    alert = await sos_service.trigger_sos(db, current_user, data)
    return TriggerSOSResponse(
        alert_id=alert.id,
        status=alert.status,
        contacted_numbers=alert.contacted_numbers or [],
        message="SOS alert triggered",
    )


@router.get("/contacts", response_model=list[EmergencyContactOut])
async def list_contacts(current_user: CurrentUserDep, db: DBDep):
    return await sos_service.list_contacts(db, current_user)


@router.post("/contacts", response_model=EmergencyContactOut)
async def upsert_contact(data: UpsertContactRequest, current_user: CurrentUserDep, db: DBDep):
    """Add or update an emergency contact (keyed on phone number)."""
    return await sos_service.upsert_contact(db, current_user, data)


@router.post("/road-assistance", response_model=RoadAssistanceResponse, status_code=201)
async def request_road_assistance(data: RoadAssistanceRequest, current_user: CurrentUserDep, db: DBDep):
    req = await sos_service.request_road_assistance(db, current_user, data)
    return RoadAssistanceResponse(
        request_id=req.id,
        status=req.status,
        provider_name=req.provider_name,
        eta_minutes=req.eta_minutes,
        message="Road assistance request submitted",
    )
