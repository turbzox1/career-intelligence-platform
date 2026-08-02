"""Authentication service: registration, login, token refresh and logout.

Implements the Service Layer pattern; depends only on repositories and
security helpers. Controllers never touch the database directly.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import ROLE_USER, User
from app.repositories.audit_repo import AuditRepository
from app.repositories.user_repo import SessionRepository, UserRepository
from app.schemas.auth import AuthResponse, LoginRequest, SignupRequest, TokenPair, UserInfo

logger = logging.getLogger("app.auth")


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class AuthService:
    """High-level authentication operations."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)
        self.sessions = SessionRepository(db)
        self.audit = AuditRepository(db)

    def signup(self, payload: SignupRequest, *, ip: str = "", ua: str = "") -> AuthResponse:
        email = payload.email.lower()
        if self.users.get_by_email(email):
            raise ConflictError("An account with this email already exists")

        user = self.users.create(
            email=email,
            full_name=payload.full_name.strip(),
            hashed_password=hash_password(payload.password),
            role=ROLE_USER,
            is_active=True,
        )
        self.db.commit()
        self.db.refresh(user)
        self.audit.log(action="user.signup", user_id=user.id, ip_address=ip, user_agent=ua)
        self.db.commit()

        logger.info("user_signed_up", extra={"user_id": user.id, "email": email})
        tokens = self._issue_tokens(user, ip=ip, ua=ua)
        return AuthResponse(user=self._user_info(user), tokens=tokens)

    def login(self, payload: LoginRequest, *, ip: str = "", ua: str = "") -> AuthResponse:
        email = payload.email.lower()
        user = self.users.get_by_email(email)
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise UnauthorizedError("Invalid credentials")
        if not user.is_active:
            raise UnauthorizedError("Account is disabled")

        self.audit.log(action="user.login", user_id=user.id, ip_address=ip, user_agent=ua)
        self.db.commit()
        logger.info("user_logged_in", extra={"user_id": user.id})
        tokens = self._issue_tokens(user, ip=ip, ua=ua)
        return AuthResponse(user=self._user_info(user), tokens=tokens)

    def refresh(self, refresh_token: str, *, ip: str = "", ua: str = "") -> AuthResponse:
        payload = decode_token(refresh_token, expected_type="refresh")
        user_id = int(payload["sub"])
        token_hash = _token_hash(refresh_token)
        session = self.sessions.get_by_token_hash(token_hash)
        if session is None or session.revoked_at is not None:
            raise UnauthorizedError("Refresh token is no longer valid")
        if session.user_id != user_id:
            raise UnauthorizedError("Refresh token mismatch")
        if _is_expired(session.expires_at):
            session.revoked_at = datetime.now(UTC)
            self.db.commit()
            raise UnauthorizedError("Refresh token has expired")

        user = self.users.get(user_id)
        if user is None or not user.is_active:
            raise UnauthorizedError("Account is unavailable")

        self.audit.log(action="user.token_refresh", user_id=user.id, ip_address=ip, user_agent=ua)
        self.db.commit()
        tokens = self._issue_tokens(user, ip=ip, ua=ua, revoke_existing=False)
        return AuthResponse(user=self._user_info(user), tokens=tokens)

    def logout(self, refresh_token: str) -> None:
        """Revoke the session associated with a refresh token."""
        payload = decode_token(refresh_token, expected_type="refresh")
        session = self.sessions.get_by_token_hash(_token_hash(refresh_token))
        if session is not None and session.revoked_at is None:
            session.revoked_at = datetime.now(UTC)
            self.db.commit()
        logger.info("user_logged_out", extra={"user_id": payload.get("sub")})

    def logout_all(self, user_id: int) -> None:
        self.sessions.revoke_all_for_user(user_id)
        self.db.commit()

    def _issue_tokens(self, user: User, *, ip: str, ua: str, revoke_existing: bool = True) -> TokenPair:
        access = create_access_token(user.id, roles=[user.role])
        refresh = create_refresh_token(user.id)

        if revoke_existing:
            self.sessions.revoke_all_for_user(user.id)

        fingerprint = _device_fingerprint(ua)
        self.sessions.create(
            user_id=user.id,
            token_hash=_token_hash(refresh),
            expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days),
            device_fingerprint=fingerprint,
            ip_address=ip[:64],
            user_agent=ua[:512],
        )
        self.db.commit()
        return TokenPair(
            access_token=access,
            refresh_token=refresh,
            expires_in=settings.access_token_expire_minutes * 60,
        )

    @staticmethod
    def _user_info(user: User) -> UserInfo:
        return UserInfo(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
        )


def _device_fingerprint(ua: str) -> str:
    if not ua:
        return "unknown"
    return hashlib.sha256(ua.encode()).hexdigest()[:32]


def _is_expired(expires_at: datetime) -> bool:
    """Timezone-safe expiry check (SQLite returns naive datetimes)."""
    now = datetime.now(UTC)
    if expires_at.tzinfo is None:
        return expires_at < now.replace(tzinfo=None)
    return expires_at < now
