"""Authentication endpoints: signup, login, refresh, logout."""

from __future__ import annotations

from fastapi import APIRouter, Request, status

from app.api.deps import CurrentUser, DbDep, client_ip
from app.api.rate_limit import limiter
from app.core.config import settings
from app.schemas.auth import AuthResponse, LoginRequest, RefreshRequest, SignupRequest
from app.schemas.common import Message
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


@limiter.limit(settings.rate_limit_auth)
@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(
    request: Request,
    payload: SignupRequest,
    db: DbDep,
) -> AuthResponse:
    """Create a new user account and return a token pair."""
    service = AuthService(db)
    return service.signup(payload, ip=client_ip(request), ua=request.headers.get("user-agent", ""))


@limiter.limit(settings.rate_limit_auth)
@router.post("/login", response_model=AuthResponse)
def login(
    request: Request,
    payload: LoginRequest,
    db: DbDep,
) -> AuthResponse:
    """Authenticate with email and password."""
    service = AuthService(db)
    return service.login(payload, ip=client_ip(request), ua=request.headers.get("user-agent", ""))


@limiter.limit(settings.rate_limit_auth)
@router.post("/refresh", response_model=AuthResponse)
def refresh(
    request: Request,
    payload: RefreshRequest,
    db: DbDep,
) -> AuthResponse:
    """Exchange a valid refresh token for a new token pair."""
    service = AuthService(db)
    return service.refresh(
        payload.refresh_token,
        ip=client_ip(request),
        ua=request.headers.get("user-agent", ""),
    )


@router.post("/logout", response_model=Message)
def logout(payload: RefreshRequest, db: DbDep) -> Message:
    """Revoke the refresh token's session."""
    AuthService(db).logout(payload.refresh_token)
    return Message(message="Logged out")


@router.post("/logout-all", response_model=Message)
def logout_all(user: CurrentUser, db: DbDep) -> Message:
    """Revoke every active session for the current user."""
    AuthService(db).logout_all(user.id)
    return Message(message="All sessions revoked")


@limiter.limit(settings.rate_limit_auth)
@router.get("/me", response_model=Message)
def me(request: Request, _user: CurrentUser) -> Message:
    """Lightweight liveness check for the authenticated session."""
    return Message(message="authenticated")
