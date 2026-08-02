"""Current-user endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbDep
from app.models.user import User
from app.schemas.common import Message
from app.schemas.user import PasswordChangeRequest, UserOut, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def get_me(user: CurrentUser) -> User:
    """Return the authenticated user's profile."""
    return user


@router.patch("/me", response_model=UserOut)
def update_me(payload: UserUpdate, user: CurrentUser, db: DbDep) -> User:
    """Update the authenticated user's profile."""
    return UserService(db).update_profile(user, payload)


@router.post("/me/change-password", response_model=Message)
def change_password(payload: PasswordChangeRequest, user: CurrentUser, db: DbDep) -> Message:
    """Change the authenticated user's password."""
    UserService(db).change_password(user, payload)
    return Message(message="Password updated")


@router.delete("/me", response_model=Message)
def deactivate_me(user: CurrentUser, db: DbDep) -> Message:
    """Deactivate (soft-disable) the authenticated account."""
    UserService(db).deactivate(user)
    return Message(message="Account deactivated")
