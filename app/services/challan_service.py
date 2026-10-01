"""Challan service — RTO sync abstraction and challan operations."""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

import httpx
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.challan import Challan, ChallanDispute
from app.models.user import User, Vehicle
from app.schemas.challan import DisputeChallanRequest


# ── RTO Integration (mockable interface) ──────────────────────────────────────
async def _fetch_challans_from_rto(registration_numbers: list[str]) -> list[dict]:
    """
    Calls the Vahan/RTO API for each vehicle registration.
    Returns a list of challan dicts. Easily mocked in tests.
    """
    if not settings.RTO_API_KEY:
        # Return mock data in dev
        return [
            {
                "challan_number": f"MOCK-{rn}-001",
                "violation_type": "Speeding > 80 km/h in 60 km/h zone",
                "violation_date": str(date.today()),
                "issued_by": "Traffic Police",
                "fine_amount": "500.00",
                "registration_number": rn,
            }
            for rn in registration_numbers[:1]  # only first vehicle in mock
        ]

    results = []
    async with httpx.AsyncClient(timeout=15) as client:
        for rn in registration_numbers:
            try:
                resp = await client.get(
                    f"{settings.RTO_API_BASE_URL}/challan",
                    params={"regNo": rn},
                    headers={"X-API-Key": settings.RTO_API_KEY},
                )
                resp.raise_for_status()
                data = resp.json()
                for item in data.get("challans", []):
                    item["registration_number"] = rn
                    results.append(item)
            except httpx.HTTPError:
                pass  # log and continue
    return results


async def sync_challans(db: AsyncSession, user: User) -> dict:
    # Collect user's vehicle registration numbers
    vehicles_result = await db.execute(
        select(Vehicle).where(Vehicle.user_id == user.id)
    )
    vehicles = vehicles_result.scalars().all()
    reg_numbers = [v.registration_number for v in vehicles]

    rto_challans = await _fetch_challans_from_rto(reg_numbers)

    new_count = 0
    for rc in rto_challans:
        challan_num = rc.get("challan_number")
        existing = await db.execute(
            select(Challan).where(Challan.challan_number == challan_num)
        )
        if existing.scalar_one_or_none():
            continue  # already imported
        challan = Challan(
            user_id=user.id,
            challan_number=challan_num,
            violation_type=rc.get("violation_type", "Unknown"),
            violation_date=date.fromisoformat(rc["violation_date"]) if rc.get("violation_date") else None,
            issued_by=rc.get("issued_by"),
            fine_amount=Decimal(str(rc.get("fine_amount", "0"))),
            rto_source_data=rc,
        )
        db.add(challan)
        new_count += 1

    await db.commit()
    return {"synced": len(rto_challans), "new_challans": new_count, "message": f"{new_count} new challans imported"}


async def list_challans(
    db: AsyncSession, user: User, offset: int = 0, limit: int = 20
) -> tuple[list[Challan], int]:
    from sqlalchemy import func, desc  # noqa: PLC0415

    count_res = await db.execute(
        select(func.count(Challan.id))
        .select_from(Challan)
        .where(Challan.user_id == user.id)
    )
    total = count_res.scalar_one()
    result = await db.execute(
        select(Challan)
        .where(Challan.user_id == user.id)
        .order_by(desc(Challan.created_at))
        .offset(offset)
        .limit(limit)
    )
    return list(result.scalars().all()), total


async def pay_challan(
    db: AsyncSession, user: User, challan_id: int, payment_method_id: int
) -> dict:
    result = await db.execute(
        select(Challan).where(Challan.id == challan_id, Challan.user_id == user.id)
    )
    challan = result.scalar_one_or_none()
    if not challan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challan not found")
    if challan.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Challan is already {challan.status}")

    # In production: call payment gateway here
    challan.status = "paid"
    challan.paid_at = datetime.now(timezone.utc)
    await db.commit()
    return {
        "challan_id": challan_id,
        "amount_paid": challan.fine_amount,
        "status": challan.status,
        "message": "Challan paid successfully",
    }


async def dispute_challan(
    db: AsyncSession, user: User, data: DisputeChallanRequest
) -> ChallanDispute:
    result = await db.execute(
        select(Challan).where(Challan.id == data.challan_id, Challan.user_id == user.id)
    )
    challan = result.scalar_one_or_none()
    if not challan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challan not found")
    if challan.status == "paid":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot dispute a paid challan")

    challan.status = "disputed"
    dispute = ChallanDispute(
        challan_id=data.challan_id,
        reason=data.reason,
        evidence_url=data.evidence_url,
    )
    db.add(dispute)
    await db.commit()
    await db.refresh(dispute)
    return dispute
