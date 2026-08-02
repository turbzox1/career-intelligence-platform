"""User persistence operations."""

from __future__ import annotations

from sqlalchemy import select

from app.models.user import Session as UserSession
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Data access for users."""

    _model = User

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email.lower())
        return self.db.scalar(stmt)


class SessionRepository(BaseRepository[UserSession]):
    """Data access for refresh-token sessions."""

    _model = UserSession

    def get_by_token_hash(self, token_hash: str) -> UserSession | None:
        stmt = select(UserSession).where(UserSession.token_hash == token_hash)
        return self.db.scalar(stmt)

    def revoke_all_for_user(self, user_id: int) -> None:
        from datetime import datetime

        from sqlalchemy import update

        self.db.execute(
            update(UserSession)
            .where(UserSession.user_id == user_id, UserSession.revoked_at.is_(None))
            .values(revoked_at=datetime.now())
        )
