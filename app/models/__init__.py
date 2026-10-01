"""All SQLAlchemy ORM models."""

from app.models.user import User, Vehicle, PaymentMethod, AppSettings  # noqa: F401
from app.models.auth import RefreshToken, PasswordResetOTP  # noqa: F401
from app.models.wallet import WalletBalance, WalletTransaction  # noqa: F401
from app.models.trip import Trip, TripTelemetry  # noqa: F401
from app.models.challan import Challan, ChallanDispute  # noqa: F401
from app.models.legal import LegalEvent  # noqa: F401
from app.models.digilocker import Document  # noqa: F401
from app.models.family import FamilyCircle, FamilyMember  # noqa: F401
from app.models.sos import EmergencyContact, SOSAlert, RoadAssistanceRequest  # noqa: F401
from app.models.bounty import BountyEvent, BountySubmission  # noqa: F401
from app.models.device import Device  # noqa: F401
from app.models.notification import Notification  # noqa: F401

__all__ = [
    "User",
    "Vehicle",
    "PaymentMethod",
    "AppSettings",
    "RefreshToken",
    "PasswordResetOTP",
    "WalletBalance",
    "WalletTransaction",
    "Trip",
    "TripTelemetry",
    "Challan",
    "ChallanDispute",
    "LegalEvent",
    "Document",
    "FamilyCircle",
    "FamilyMember",
    "EmergencyContact",
    "SOSAlert",
    "RoadAssistanceRequest",
    "BountyEvent",
    "BountySubmission",
    "Device",
    "Notification",
]
