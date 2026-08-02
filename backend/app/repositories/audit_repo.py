"""Audit log persistence."""

from __future__ import annotations

from app.models.audit import AuditLog
from app.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    """Data access for audit logs."""

    _model = AuditLog

    def log(
        self,
        *,
        action: str,
        user_id: int | None = None,
        entity_type: str = "",
        entity_id: int | None = None,
        ip_address: str = "",
        user_agent: str = "",
        meta: dict | None = None,
    ) -> AuditLog:
        return self.create(
            action=action,
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            ip_address=ip_address[:64],
            user_agent=user_agent[:512],
            meta=meta or {},
        )
