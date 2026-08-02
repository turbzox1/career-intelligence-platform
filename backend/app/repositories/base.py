"""Generic base repository implementing common data-access operations.

Concrete repositories inherit from :class:`BaseRepository` and may override
the ``_model`` attribute. This keeps persistence concerns isolated from the
service layer (Repository Pattern).
"""

from __future__ import annotations

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.db.base import Base


class BaseRepository[ModelT: Base]:
    """CRUD helpers for a single SQLAlchemy model."""

    _model: type[ModelT]

    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, entity_id: int) -> ModelT | None:
        return self.db.get(self._model, entity_id)

    def create(self, **kwargs: object) -> ModelT:
        obj = self._model(**kwargs)
        self.db.add(obj)
        self.db.flush()
        return obj

    def save(self, obj: ModelT) -> ModelT:
        self.db.add(obj)
        self.db.flush()
        return obj

    def delete(self, obj: ModelT) -> None:
        self.db.delete(obj)
        self.db.flush()

    def list(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        filters: dict | None = None,
        order_by: str | None = None,
    ) -> tuple[list[ModelT], int]:
        """Return (items, total_count) with optional filtering and ordering."""
        stmt = select(self._model)
        if filters:
            for key, value in filters.items():
                column = getattr(self._model, key, None)
                if column is not None and value is not None:
                    stmt = stmt.where(column == value)

        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        if order_by:
            stmt = stmt.order_by(self._order_expr(order_by, self._model))
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        return list(self.db.scalars(stmt).all()), total

    @staticmethod
    def _order_expr(spec: str, model: type) -> object:
        """Translate an 'col.desc()' / 'col.asc()' spec into a SQL expression."""
        spec = spec.strip()
        for direction in ("desc", "asc"):
            suffix = f".{direction}()"
            if spec.endswith(suffix):
                column = getattr(model, spec[: -len(suffix)])
                return column.desc() if direction == "desc" else column.asc()
        return text(spec)
