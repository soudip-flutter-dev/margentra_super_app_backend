# MargNetra Super App — Python FastAPI Backend

Production-grade backend for the **MargNetra Super App** — a driving-behaviour rewards, e-Challan, Legal Vault, DigiLocker, Family Circle, Emergency SOS, Bounty Capture, BLE/OBD device, and MGC Wallet platform.

> 📖 **Comprehensive API Documentation & Architecture Flows:** See [API_DOCUMENTATION_AND_FLOWS.md](API_DOCUMENTATION_AND_FLOWS.md) for individual endpoint specifications, request/response schemas, step-by-step backend execution flows, and sequence diagrams.

---

## ⚡ Quick Start (Local Dev)

### 1. Clone & configure

```bash
git clone <repo-url>
cd margentra_super_app_backend_python
cp .env.example .env
# Edit .env with your DB, Redis, S3, RTO API keys
```

### 2. Create a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### 3. Start PostgreSQL + Redis (Docker shortcut)

```bash
docker compose up postgres redis -d
```

### 4. Run Alembic migrations

```bash
alembic upgrade head
```

### 5. Start the dev server

```bash
uvicorn app.main:app --reload
```

Open **http://localhost:8000/docs** for interactive Swagger UI.

---

## 🐳 Full Docker Stack

```bash
docker compose up --build
```

This starts:
| Container | Port | Description |
|---|---|---|
| `margnetra_app` | 8000 | FastAPI + Uvicorn (4 workers) |
| `margnetra_postgres` | 5432 | PostgreSQL 16 |
| `margnetra_redis` | 6379 | Redis 7 |
| `margnetra_celery` | — | Celery background worker |

---

## 🧪 Running Tests

```bash
# Install test extras (aiosqlite for in-memory test DB)
pip install aiosqlite

pytest -v
```

Tests use an **in-memory SQLite** database — no external services required.

---

## 📁 Project Structure

```
app/
├── main.py                  # FastAPI app, lifespan, middleware
├── core/
│   ├── config.py             # pydantic-settings (.env)
│   ├── security.py           # JWT + bcrypt
│   └── dependencies.py       # get_db, get_current_user, pagination
├── db/
│   ├── base.py               # SQLAlchemy Base + model imports
│   ├── session.py            # Async engine
│   └── init_db.py            # Table creation on startup
├── models/                   # SQLAlchemy ORM (one file per domain)
├── schemas/                  # Pydantic v2 request/response schemas
├── api/v1/
│   ├── router.py             # Aggregates all routers at /api/v1
│   └── endpoints/            # 13 domain routers + WebSocket router
├── services/                 # Business logic layer
├── ws/                       # WebSocket connection manager + event helpers
└── utils/                    # Pagination helper, exception classes
```

---

## 🔌 API Route Map (50 Endpoints)

| Domain | Method | Path |
|---|---|---|
| **Auth** | POST | `/api/v1/auth/register` |
| | POST | `/api/v1/auth/login` |
| | POST | `/api/v1/auth/forgot-password` |
| | POST | `/api/v1/auth/reset-password` |
| | POST | `/api/v1/auth/logout` |
| | POST | `/api/v1/auth/refresh` |
| **User** | GET/PUT | `/api/v1/user/profile` |
| | GET | `/api/v1/user/civil-score` |
| | GET/POST | `/api/v1/user/vehicles` |
| | GET/POST | `/api/v1/user/payment-methods` |
| | GET/PUT | `/api/v1/user/settings` |
| | POST | `/api/v1/user/avatar` |
| **Wallet** | GET | `/api/v1/wallet/balance` |
| | GET | `/api/v1/wallet/transactions` |
| | POST | `/api/v1/wallet/redeem/fastag` |
| | POST | `/api/v1/wallet/buy/streak-protection` |
| **Trip** | POST | `/api/v1/trip/start` |
| | POST | `/api/v1/trip/end` |
| | POST | `/api/v1/trip/telemetry` |
| | GET | `/api/v1/trip/earnings/current` |
| | GET | `/api/v1/trip/history` |
| | WS | `/api/v1/ws/trip/live` |
| **Challan** | GET | `/api/v1/challan/list` |
| | POST | `/api/v1/challan/sync` |
| | POST | `/api/v1/challan/pay` |
| | POST | `/api/v1/challan/dispute` |
| **Legal** | GET | `/api/v1/legal/events` |
| | POST | `/api/v1/legal/events/upload` |
| | GET | `/api/v1/legal/events/{id}/export` |
| **DigiLocker** | GET | `/api/v1/digilocker/documents` |
| | POST | `/api/v1/digilocker/documents/upload` |
| | GET | `/api/v1/digilocker/alerts` |
| **Family** | GET | `/api/v1/family/members` |
| | POST | `/api/v1/family/invite` |
| | GET | `/api/v1/family/members/{id}/location` |
| | WS | `/api/v1/ws/family/live` |
| **SOS** | POST | `/api/v1/sos/trigger` |
| | GET/POST | `/api/v1/sos/contacts` |
| | POST | `/api/v1/sos/road-assistance` |
| **Bounty** | GET | `/api/v1/bounty/events` |
| | POST | `/api/v1/bounty/submit` |
| **Devices** | POST | `/api/v1/devices/register` |
| | GET | `/api/v1/devices/list` |
| **Notifications** | GET | `/api/v1/notifications` |
| | PUT | `/api/v1/notifications/{id}/read` |

---

## 🔐 Authentication

All routes except `/api/v1/auth/*` require:

```
Authorization: Bearer <access_token>
```

- Access tokens expire in **30 minutes** (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- Refresh tokens valid for **30 days**, stored hashed in DB for revocation
- Passwords hashed with **bcrypt** — never stored or returned in plaintext

---

## ⚙️ Key Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | Async PostgreSQL URL | `postgresql+asyncpg://...` |
| `JWT_SECRET_KEY` | JWT signing secret | *(required)* |
| `REDIS_URL` | Redis connection | `redis://localhost:6379/0` |
| `USE_LOCAL_STORAGE` | Use disk instead of S3 | `true` |
| `RTO_API_KEY` | Vahan/RTO API key | *(optional — uses mock if blank)* |
| `MGC_PER_KM_RATE` | MGC coins per km driven | `1.5` |
| `MGC_STREAK_PROTECTION_COST` | Cost to protect streak | `50` |

See `.env.example` for the full list.

---

## 🧮 Business Logic Highlights

### Civil Score Engine (`trip_service.py`)
- Base delta: `+0.05 × distance_km`
- Harsh braking: `-2.0` per event
- Harsh acceleration: `-1.5` per event
- Over-speed: `-3.0` per event
- Clamped to `[-20, +10]` per trip

### MGC Earning Formula
- Base: `distance_km × MGC_PER_KM_RATE`
- Streak bonus: `+10%` if streak ≥ `MGC_BONUS_STREAK_DAYS`

### SHA-256 Legal Certification (Sec 65B)
- On upload, video bytes are hashed → stored as `video_sha256`
- Export generates a ReportLab PDF affidavit embedding the hash
- Chain of custody is preserved without storing raw video in DB

### RTO Sync
- `challan_service._fetch_challans_from_rto()` abstracts the Vahan API
- Returns **mock data** when `RTO_API_KEY` is blank (dev mode)
- Easy to mock in tests via `unittest.mock.patch`

---

## 🌐 WebSocket API

### Trip Live Telemetry
```
ws://localhost:8000/api/v1/ws/trip/live?token=<jwt>&trip_id=<id>
```
**Server pushes:**
```json
{"event": "telemetry", "data": {"speed": 60, "rpm": 2500, "g_force": 0.1, "engine_temp": 92, "timestamp": "..."}}
```

### Family Live Location
```
ws://localhost:8000/api/v1/ws/family/live?token=<jwt>&family_circle_id=<id>
```
**Members push (client → server):**
```json
{"type": "location_update", "data": {"lat": 12.97, "lng": 77.59}}
```
**Server broadcasts:**
```json
{"event": "location_update", "data": {"user_id": "42", "lat": 12.97, "lng": 77.59}}
```

---

## 📜 Alembic Migrations

```bash
# Generate a new migration after model changes
alembic revision --autogenerate -m "describe change"

# Apply all pending migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1
```
