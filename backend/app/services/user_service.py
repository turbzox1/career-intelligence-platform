"""User profile service operations."""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedError
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import PasswordChangeRequest, UserUpdate

logger = logging.getLogger("app.users")


class UserService:
    """Profile management operations."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)

    def update_profile(self, user: User, payload: UserUpdate) -> User:
        if payload.full_name is not None:
            user.full_name = payload.full_name.strip()
        if payload.profile is not None:
            merged = dict(user.profile or {})
            merged.update(payload.profile)
            user.profile = merged
        self.db.commit()
        self.db.refresh(user)
        logger.info("profile_updated", extra={"user_id": user.id})
        return user

    def change_password(self, user: User, payload: PasswordChangeRequest) -> None:
        if not verify_password(payload.current_password, user.hashed_password):
            raise UnauthorizedError("Current password is incorrect")
        user.hashed_password = hash_password(payload.new_password)
        self.db.commit()
        logger.info("password_changed", extra={"user_id": user.id})

    def deactivate(self, user: User) -> User:
        user.is_active = False
        self.db.commit()
        self.db.refresh(user)
        return user
