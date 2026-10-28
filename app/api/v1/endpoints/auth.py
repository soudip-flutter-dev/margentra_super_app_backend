"""Auth endpoints: register, login, logout, forgot/reset password, refresh."""

from fastapi import APIRouter, Request

from app.core.dependencies import DBDep
from app.core.limiter import limiter
from app.schemas.auth import (
    AccessTokenResponse,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.schemas.common import MessageResponse
from app.schemas.user import UserProfileOut
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserProfileOut, status_code=201)
async def register_user(data: RegisterRequest, db: DBDep):
    
    """Register a new MargNetra user."""
    user = await auth_service.register_user(db, data)
    print("Registration hit>>>>>>>>>>>", user.email, user.phone, user.full_name)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: DBDep, request: Request):
    """Authenticate and receive JWT access + refresh tokens."""
    ident = data.phone or data.email or data.username or data.identifier or data.phone_number or data.login
    print(f"Login hit >>>>>>>>>>> identifier={ident}", flush=True)
    return await auth_service.login_user(db, data)


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(data: ForgotPasswordRequest, db: DBDep, request: Request):
    """Send OTP to registered phone for password reset."""
    msg = await auth_service.forgot_password(db, data.phone)
    return {"message": msg}


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(data: ResetPasswordRequest, db: DBDep):
    """Reset password using OTP received on phone."""
    await auth_service.reset_password(db, data)
    return {"message": "Password reset successfully"}


@router.post("/logout", response_model=MessageResponse)
async def logout(data: LogoutRequest, db: DBDep):
    """Revoke refresh token (client should also discard access token)."""
    await auth_service.logout_user(db, data.refresh_token)
    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("10/minute")
async def refresh_token(request: Request, data: RefreshTokenRequest, db: DBDep):
    """Exchange a valid refresh token for a new access token and rotated refresh token."""
    result = await auth_service.refresh_access_token(db, data.refresh_token)
    return result
