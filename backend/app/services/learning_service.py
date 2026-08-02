"""Learning recommendation engine service."""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.data.learning_catalog import resources_for_skill
from app.models.user import User
from app.repositories.learning_repo import LearningResourceRepository, RecommendationRepository
from app.schemas.learning import (
    LearningResourceOut,
    LearningRoadmapResponse,
    RecommendationOut,
    RoadmapStep,
)

logger = logging.getLogger("app.services.learning")


class LearningService:
    """Builds learning recommendations and personalised roadmaps."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.resources = LearningResourceRepository(db)
        self.recommendations = RecommendationRepository(db)

    def recommend_for_missing_skills(self, user: User, missing_skills: list[dict]) -> list[RecommendationOut]:
        """Persist and return learning recommendations for missing skills.

        ``missing_skills`` is a list of dicts with ``skill`` and
        ``priority_score`` (as produced by the skill-gap service).
        """
        self.recommendations.clear_for_user(user.id)
        results: list[RecommendationOut] = []

        ordered = sorted(missing_skills, key=lambda x: x.get("priority_score", 0), reverse=True)
        for rank, item in enumerate(ordered, start=1):
            skill = item["skill"]
            resource_data = resources_for_skill(skill)
            if not resource_data:
                continue
            resource = self.resources.get_by_url(resource_data[0]["url"]) or self.resources.create(
                **self._to_orm_kwargs(resource_data[0])
            )
            reason = (
                f"'{skill}' is a high-priority missing skill for your target role "
                f"(priority score {item.get('priority_score', 0):.2f})."
            )
            rec = self.recommendations.create(
                user_id=user.id,
                resource_id=resource.id,
                skill_name=skill,
                reason=reason,
                score=item.get("priority_score", 0.5),
                priority=rank,
            )
            results.append(
                RecommendationOut(
                    id=rec.id,
                    skill_name=skill,
                    reason=reason,
                    score=rec.score,
                    status=rec.status,
                    priority=rec.priority,
                    resource=LearningResourceOut.model_validate(resource),
                )
            )
        self.db.commit()
        logger.info("recommendations_created", extra={"user_id": user.id, "count": len(results)})
        return results

    def list_recommendations(self, user: User, *, limit: int = 50) -> list[RecommendationOut]:
        rows = self.recommendations.list_for_user(user.id, limit=limit)
        return [
            RecommendationOut(
                id=row.id,
                skill_name=row.skill_name,
                reason=row.reason,
                score=row.score,
                status=row.status,
                priority=row.priority,
                resource=LearningResourceOut.model_validate(row.resource),
            )
            for row in rows
        ]

    def build_roadmap(self, missing_skills: list[str], daily_hours: float) -> LearningRoadmapResponse:
        steps: list[RoadmapStep] = []
        for rank, skill in enumerate(missing_skills, start=1):
            resources = [
                LearningResourceOut(
                    id=0,
                    skill_name=r["skill"],
                    title=r["title"],
                    provider=r["provider"],
                    url=r["url"],
                    resource_type=r["resource_type"],
                    difficulty=r["difficulty"],
                    estimated_hours=r["estimated_hours"],
                    rating=r.get("rating"),
                )
                for r in resources_for_skill(skill)
            ]
            total_hours = sum(r.estimated_hours for r in resources[:2]) or 8.0
            steps.append(
                RoadmapStep(
                    skill=skill,
                    priority=rank,
                    estimated_hours=round(total_hours, 1),
                    resources=resources,
                )
            )
        total_hours = round(sum(s.estimated_hours for s in steps), 1)
        estimated_weeks = round(max(total_hours / max(daily_hours, 0.25) / 5, 0.5), 1)
        return LearningRoadmapResponse(
            total_estimated_hours=total_hours,
            estimated_weeks=estimated_weeks,
            steps=steps,
        )

    @staticmethod
    def _to_orm_kwargs(resource: dict) -> dict:
        """Map catalog fields onto the ORM column names."""
        return {
            "skill_name": resource["skill"],
            "title": resource["title"],
            "provider": resource["provider"],
            "url": resource["url"],
            "resource_type": resource["resource_type"],
            "difficulty": resource["difficulty"],
            "estimated_hours": resource["estimated_hours"],
            "rating": resource.get("rating"),
            "tags": list(resource.get("tags", ())),
        }
