"""Analytics dashboard endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbDep
from app.schemas.analytics import AnalyticsResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=AnalyticsResponse)
def dashboard(user: CurrentUser, db: DbDep) -> AnalyticsResponse:
    """Return aggregated analytics for the current user's dashboard."""
    return AnalyticsService(db).dashboard(user.id)
