"""Shared FastAPI dependencies: database, authentication and rate limiting."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repo import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)

DbDep = Annotated[Session, Depends(get_db)]


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: DbDep,
) -> User:
    """Resolve the authenticated user from a valid access token."""
    if credentials is None:
        raise UnauthorizedError("Authentication required")
    try:
        payload = decode_token(credentials.credentials, expected_type="access")
    except UnauthorizedError:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        raise UnauthorizedError("Invalid token") from exc

    user_id = int(payload["sub"])
    user = UserRepository(db).get(user_id)
    if user is None or not user.is_active:
        raise UnauthorizedError("Account is unavailable")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*roles: str):
    """Dependency factory enforcing role-based access control."""

    def _checker(user: CurrentUser) -> User:
        if user.role not in roles:
            raise ForbiddenError("Insufficient permissions")
        return user

    return _checker


def client_ip(request: Request) -> str:
    """Best-effort client IP extraction behind reverse proxies."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else ""
