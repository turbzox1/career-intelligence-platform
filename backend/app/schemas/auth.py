"""Authentication request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, field_validator


class SignupRequest(BaseModel):
    """Payload for creating a new user account."""

    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def _password_strength(cls, value: str) -> str:
        if not any(ch.isdigit() for ch in value):
            raise ValueError("Password must contain at least one digit")
        if not any(ch.isalpha() for ch in value):
            raise ValueError("Password must contain at least one letter")
        return value


class LoginRequest(BaseModel):
    """Payload for signing in."""

    email: EmailStr
    password: str = Field(min_length=1)


class RefreshRequest(BaseModel):
    """Payload for refreshing an expired access token."""

    refresh_token: str = Field(min_length=1)


class TokenPair(BaseModel):
    """JWT access + refresh token pair."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserInfo(BaseModel):
    """Lightweight user identity embedded in auth responses."""

    id: int
    email: EmailStr
    full_name: str
    role: str


class AuthResponse(BaseModel):
    """Authentication response envelope."""

    user: UserInfo
    tokens: TokenPair
