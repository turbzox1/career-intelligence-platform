"""Learning resource and recommendation persistence operations."""

from __future__ import annotations

from sqlalchemy import select

from app.models.learning import LearningResource, Recommendation
from app.repositories.base import BaseRepository


class LearningResourceRepository(BaseRepository[LearningResource]):
    """Data access for the learning resource catalog."""

    _model = LearningResource

    def get_by_url(self, url: str) -> LearningResource | None:
        stmt = select(LearningResource).where(LearningResource.url == url)
        return self.db.scalar(stmt)

    def get_by_skills(self, skill_names: list[str], *, limit: int = 50) -> list[LearningResource]:
        if not skill_names:
            return []
        stmt = select(LearningResource).where(LearningResource.skill_name.in_(skill_names)).limit(limit)
        return list(self.db.scalars(stmt).all())


class RecommendationRepository(BaseRepository[Recommendation]):
    """Data access for per-user learning recommendations."""

    _model = Recommendation

    def list_for_user(self, user_id: int, *, limit: int = 50, status: str | None = None) -> list[Recommendation]:
        stmt = select(Recommendation).where(Recommendation.user_id == user_id)
        if status:
            stmt = stmt.where(Recommendation.status == status)
        stmt = stmt.order_by(Recommendation.priority.asc()).limit(limit)
        return list(self.db.scalars(stmt).all())

    def clear_for_user(self, user_id: int) -> None:
        from sqlalchemy import delete

        self.db.execute(delete(Recommendation).where(Recommendation.user_id == user_id))
