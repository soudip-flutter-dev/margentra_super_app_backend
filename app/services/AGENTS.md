# Services

## Overview

Core business logic for MargNetra. It handles driver rewards, trip telemetry heuristics, legal affidavits, and external integrations.

## Key files

| File | Owns |
|---|---|
| app/services/auth_service.py | User registration, password verification, OTP login, and tokens |
| app/services/trip_service.py | Trip lifecycles, telemetry ingestion, civil score, and coin rewards |
| app/services/challan_service.py | Vehicle challan lookup, mock RTO APIs, and dispute submissions |
| app/services/wallet_service.py | Coins ledger, user balance checks, and reward redemptions |
| app/services/legal_service.py | Evidence vault, SHA 256 hashing, and Section 65B affidavit PDFs |
| app/services/sos_service.py | Emergency broadcasts, alerts to family circle, and sirens |

## Conventions

- Keep endpoint routers thin and move business calculations into services
- Use AsyncSession explicitly in all database queries
- Check for existing active trips before starting a new one
- Protect wallet updates by verifying positive balances before debiting
- Provide mock data fallbacks when third party API credentials are not set

## Gotchas

- Civil score delta is capped between minus twenty and plus ten per trip
- Section 65B affidavit generation falls back to a text stub if ReportLab is missing
- In development, local file storage serves uploads instead of AWS S3

## Agent skills

Declined: FastAPI, SQLAlchemy, Alembic, Redis, Pytest

_Drafted by /audit from the repo, worth a quick human pass. Edit freely: once a line stops matching this draft, later runs treat it as curated and will flag rather than overwrite it._
