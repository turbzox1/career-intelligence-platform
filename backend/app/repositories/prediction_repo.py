"""Prediction persistence operations."""

from __future__ import annotations

from sqlalchemy import func, select

from app.models.prediction import Prediction, PredictionHistory
from app.repositories.base import BaseRepository


class PredictionRepository(BaseRepository[Prediction]):
    """Data access for salary predictions."""

    _model = Prediction

    def list_for_user(self, user_id: int, *, page: int = 1, page_size: int = 20) -> tuple[list[Prediction], int]:
        filters = {"user_id": user_id}
        return self.list(page=page, page_size=page_size, filters=filters, order_by="id.desc()")

    def get_for_user(self, prediction_id: int, user_id: int) -> Prediction | None:
        stmt = select(Prediction).where(Prediction.id == prediction_id, Prediction.user_id == user_id)
        return self.db.scalar(stmt)


class PredictionHistoryRepository(BaseRepository[PredictionHistory]):
    """Data access for the append-only analytics snapshot."""

    _model = PredictionHistory

    def count_for_user(self, user_id: int) -> int:
        stmt = select(func.count()).select_from(PredictionHistory).where(PredictionHistory.user_id == user_id)
        return int(self.db.scalar(stmt) or 0)

    def avg_salary_for_user(self, user_id: int) -> float:
        stmt = select(func.avg(PredictionHistory.predicted_salary)).where(PredictionHistory.user_id == user_id)
        return float(self.db.scalar(stmt) or 0.0)

    def group_by(self, user_id: int, column: str) -> list[tuple[str, float, int]]:
        col = getattr(PredictionHistory, column)
        stmt = (
            select(col, func.avg(PredictionHistory.predicted_salary), func.count())
            .where(PredictionHistory.user_id == user_id)
            .group_by(col)
        )
        return [(str(k), float(avg), int(cnt)) for k, avg, cnt in self.db.execute(stmt)]

    def trend(self, user_id: int) -> list[tuple[str, float]]:
        dialect = self.db.bind.dialect.name if self.db.bind else "postgresql"
        day_expr = (
            func.date(PredictionHistory.created_at)
            if dialect == "sqlite"
            else func.to_char(PredictionHistory.created_at, "YYYY-MM-DD")
        )
        stmt = (
            select(
                day_expr,
                func.avg(PredictionHistory.predicted_salary),
            )
            .where(PredictionHistory.user_id == user_id)
            .group_by(day_expr)
            .order_by(day_expr)
        )
        return [(str(day), float(avg)) for day, avg in self.db.execute(stmt)]
