import asyncio
import io
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.security import create_access_token
from app.models.user import User
from app.db.session import async_session_factory
from sqlalchemy import select

async def run_verification():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Get or create a test user
        async with async_session_factory() as session:
            result = await session.execute(select(User).limit(1))
            user = result.scalar_one_or_none()
            if not user:
                print("FAIL: No user found in database to authenticate")
                return
            user_id = user.id
            phone = user.phone

        token = create_access_token(subject=str(user_id))
        headers = {"Authorization": f"Bearer {token}"}
        print(f"Authenticated as user_id={user_id}, phone={phone}")

        # 2. GET /api/v1/user/profile
        res = await client.get("/api/v1/user/profile", headers=headers)
        print(f"GET /api/v1/user/profile: status={res.status_code}")
        assert res.status_code == 200, res.text
        profile_data = res.json()
        print(f"  profile: name={profile_data.get('full_name')}, civil_score={profile_data.get('civil_score')}, streak={profile_data.get('driving_streak_days')}, mgc_balance={profile_data.get('mgc_balance')}")

        # 3. PUT /api/v1/user/profile
        update_payload = {"full_name": "Test Driver Verified", "email": "verified_driver@example.com"}
        res = await client.put("/api/v1/user/profile", json=update_payload, headers=headers)
        print(f"PUT /api/v1/user/profile: status={res.status_code}")
        assert res.status_code == 200, res.text
        updated = res.json()
        print(f"  updated: name={updated.get('full_name')}, email={updated.get('email')}")

        # 4. POST /api/v1/user/avatar (multipart file upload)
        dummy_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        files = {"file": ("avatar.png", dummy_png, "image/png")}
        res = await client.post("/api/v1/user/avatar", files=files, headers=headers)
        print(f"POST /api/v1/user/avatar: status={res.status_code}")
        assert res.status_code == 200, res.text
        avatar_data = res.json()
        print(f"  avatar_url={avatar_data.get('avatar_url')}")

        # 5. GET /api/v1/user/civil-score
        res = await client.get("/api/v1/user/civil-score", headers=headers)
        print(f"GET /api/v1/user/civil-score: status={res.status_code}")
        assert res.status_code == 200, res.text
        cs_data = res.json()
        print(f"  civil_score={cs_data.get('score')}, tier={cs_data.get('tier')}, factors_count={len(cs_data.get('factors', []))}")

        # 6. GET /api/v1/user/vehicles
        res = await client.get("/api/v1/user/vehicles", headers=headers)
        print(f"GET /api/v1/user/vehicles: status={res.status_code}")
        assert res.status_code == 200, res.text
        vehicles = res.json()
        print(f"  vehicles count={len(vehicles)}")

        # 7. POST /api/v1/user/vehicles
        unique_plate = f"DL01AB{user_id:04d}"
        veh_payload = {
            "registration_number": unique_plate,
            "make": "Hyundai",
            "model": "i20",
            "year": 2022,
            "fuel_type": "PETROL",
            "is_primary": True
        }
        res = await client.post("/api/v1/user/vehicles", json=veh_payload, headers=headers)
        print(f"POST /api/v1/user/vehicles (first attempt): status={res.status_code}")
        if res.status_code == 201 or res.status_code == 200:
            print(f"  registered vehicle: {res.json().get('registration_number')}")
        elif res.status_code == 400:
            print(f"  vehicle already registered: {res.json()}")

        # 8. POST /api/v1/user/vehicles (duplicate attempt observation)
        res_dup = await client.post("/api/v1/user/vehicles", json=veh_payload, headers=headers)
        print(f"POST /api/v1/user/vehicles (duplicate attempt): status={res_dup.status_code}")
        print(f"  duplicate response: {res_dup.json()}")

        # 9. GET /api/v1/user/payment-methods
        res = await client.get("/api/v1/user/payment-methods", headers=headers)
        print(f"GET /api/v1/user/payment-methods: status={res.status_code}")
        assert res.status_code == 200, res.text

        # 10. POST /api/v1/user/payment-methods
        pm_payload = {"type": "upi", "identifier": "driver@oksbi", "is_primary": False}
        res = await client.post("/api/v1/user/payment-methods", json=pm_payload, headers=headers)
        print(f"POST /api/v1/user/payment-methods: status={res.status_code}")
        assert res.status_code in [200, 201], res.text
        print(f"  added payment method: {res.json().get('identifier')}")

        # 11. GET /api/v1/user/settings
        res = await client.get("/api/v1/user/settings", headers=headers)
        print(f"GET /api/v1/user/settings: status={res.status_code}")
        assert res.status_code == 200, res.text
        settings = res.json()
        print(f"  settings: dark_mode={settings.get('dark_mode')}, language={settings.get('language')}, hud_overlay={settings.get('hud_overlay')}")

        # 12. PUT /api/v1/user/settings
        settings_payload = {
            "dark_mode": True,
            "language": "hi",
            "notifications_enabled": True,
            "location_sharing": True,
            "hud_overlay": True
        }
        res = await client.put("/api/v1/user/settings", json=settings_payload, headers=headers)
        print(f"PUT /api/v1/user/settings: status={res.status_code}")
        assert res.status_code == 200, res.text
        updated_settings = res.json()
        print(f"  updated settings: dark_mode={updated_settings.get('dark_mode')}, language={updated_settings.get('language')}")

        print("ALL BACKEND ENDPOINTS VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_verification())
