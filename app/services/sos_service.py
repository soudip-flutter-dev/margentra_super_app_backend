"""SOS service — trigger alerts, manage contacts, road assistance."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sos import EmergencyContact, RoadAssistanceRequest, SOSAlert
from app.models.user import User
from app.schemas.sos import RoadAssistanceRequest as RoadAssistanceSchema, TriggerSOSRequest, UpsertContactRequest


async def trigger_sos(
    db: AsyncSession, user: User, data: TriggerSOSRequest
) -> SOSAlert:
    # Gather emergency contact numbers
    contacts_res = await db.execute(
        select(EmergencyContact).where(EmergencyContact.user_id == user.id)
    )
    contacts = contacts_res.scalars().all()
    numbers = [c.phone for c in contacts]

    # In production: send SMS/call via Twilio or similar
    alert = SOSAlert(
        user_id=user.id,
        latitude=data.latitude,
        longitude=data.longitude,
        message=data.message,
        status="triggered",
        contacted_numbers=numbers,
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return alert


async def list_contacts(db: AsyncSession, user: User) -> list[EmergencyContact]:
    result = await db.execute(
        select(EmergencyContact).where(EmergencyContact.user_id == user.id)
    )
    return list(result.scalars().all())


async def upsert_contact(
    db: AsyncSession, user: User, data: UpsertContactRequest
) -> EmergencyContact:
    # Check if contact with same phone already exists
    existing = await db.execute(
        select(EmergencyContact).where(
            EmergencyContact.user_id == user.id,
            EmergencyContact.phone == data.phone,
        )
    )
    contact = existing.scalar_one_or_none()
    if contact:
        contact.name = data.name
        contact.relation = data.relation
        contact.is_primary = data.is_primary
    else:
        contact = EmergencyContact(
            user_id=user.id,
            name=data.name,
            phone=data.phone,
            relation=data.relation,
            is_primary=data.is_primary,
        )
        db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def request_road_assistance(
    db: AsyncSession, user: User, data: RoadAssistanceSchema
) -> RoadAssistanceRequest:
    req = RoadAssistanceRequest(
        user_id=user.id,
        latitude=data.latitude,
        longitude=data.longitude,
        issue_type=data.issue_type,
        description=data.description,
        status="pending",
        provider_name="MargNetra Roadside",
        eta_minutes=30,
    )
    db.add(req)
    await db.commit()
    await db.refresh(req)
    return req
