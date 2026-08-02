"""Health and readiness endpoints for orchestration and monitoring."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AppError
from app.db.session import get_db

router = APIRouter(tags=["health"])

logger = logging.getLogger("app.health")


@router.get("/health/live")
def liveness() -> dict:
    """Liveness probe: the process is up."""
    return {"status": "ok"}


@router.get("/health/ready")
def readiness(db: Session = Depends(get_db)) -> dict:
    """Readiness probe: verifies database connectivity."""
    checks: dict[str, str] = {}
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:  # pragma: no cover
        logger.warning("readiness db check failed: %s", exc)
        checks["database"] = "unavailable"

    redis_status = "skipped"
    try:
        import redis

        client = redis.Redis.from_url(settings.resolved_redis_url, socket_timeout=2)
        client.ping()
        redis_status = "ok"
    except Exception as exc:  # pragma: no cover
        logger.warning("readiness redis check failed: %s", exc)
        redis_status = "unavailable"

    checks["redis"] = redis_status
    ready = all(v == "ok" for v in checks.values())
    if not ready:
        raise AppError("Service not ready", status_code=503, code="not_ready", details=checks)
    return {"status": "ready", "checks": checks}
