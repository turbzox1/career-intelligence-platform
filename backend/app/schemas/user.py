"""User profile schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserOut(BaseModel):
    """Public user representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    created_at: datetime


class UserUpdate(BaseModel):
    """Fields a user may update on their own profile."""

    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    profile: dict | None = None


class PasswordChangeRequest(BaseModel):
    """Change-password payload."""

    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8, max_length=128)
