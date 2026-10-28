"""Pydantic schemas for auth endpoints."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator, model_validator

from app.schemas.user import UserProfileOut


class RegisterRequest(BaseModel):
    full_name: str
    phone: str
    email: EmailStr | None = None
    password: str
    confirm_password: str | None = None

    @model_validator(mode="after")
    def passwords_match(self) -> "RegisterRequest":
        if self.confirm_password is not None and self.password != self.confirm_password:
            raise ValueError("password and confirm_password do not match")
        return self

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not v.lstrip("+").isdigit() or len(v) < 7:
            raise ValueError("Invalid phone number format")
        return v

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    phone: str | None = None
    email: str | None = None
    username: str | None = None
    identifier: str | None = None
    phone_number: str | None = None
    login: str | None = None
    password: str

    @model_validator(mode="after")
    def validate_identifier(self) -> "LoginRequest":
        raw = (
            self.phone
            or self.email
            or self.username
            or self.identifier
            or self.phone_number
            or self.login
        )
        if not raw or not str(raw).strip():
            raise ValueError("Please provide either 'phone' or 'email' to login")
        return self


class ForgotPasswordRequest(BaseModel):
    phone: str


class ResetPasswordRequest(BaseModel):
    phone: str
    otp: str
    new_password: str
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self) -> "ResetPasswordRequest":
        if self.new_password != self.confirm_password:
            raise ValueError("new_password and confirm_password do not match")
        return self


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: Optional["UserProfileOut"] = None


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
