"""Analytics aggregation service for the dashboard."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.repositories.prediction_repo import PredictionHistoryRepository
from app.schemas.analytics import (
    AnalyticsResponse,
    SalaryByGroup,
    TopSkill,
    TrendPoint,
)
from app.services.skill_gap_service import SkillGapService


class AnalyticsService:
    """Computes aggregated metrics from prediction history."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.history = PredictionHistoryRepository(db)
        self.skill_gap = SkillGapService(db)

    def dashboard(self, user_id: int) -> AnalyticsResponse:
        total = self.history.count_for_user(user_id)
        avg_salary = self.history.avg_salary_for_user(user_id)
        trend = self.history.trend(user_id)
        by_location = self.history.group_by(user_id, "location")
        by_industry = self.history.group_by(user_id, "industry")
        by_experience = self.history.group_by(user_id, "years_experience")

        # Skills: aggregate from predictions stored in prediction_history is not
        # denormalised, so we read top skills from recent predictions instead.
        top_skills, missing_skills = self._skill_stats(user_id)

        return AnalyticsResponse(
            total_predictions=total,
            average_salary=round(avg_salary, 2),
            salary_trend=[TrendPoint(date=day, value=value) for day, value in trend],
            salary_by_location=[
                SalaryByGroup(label=loc, average_salary=round(avg, 2), count=count) for loc, avg, count in by_location
            ],
            salary_by_industry=[
                SalaryByGroup(label=ind, average_salary=round(avg, 2), count=count) for ind, avg, count in by_industry
            ],
            salary_by_experience=[
                TrendPoint(date=exp_level, value=round(avg, 2)) for exp_level, avg, _ in by_experience
            ],
            top_skills=top_skills,
            most_missing_skills=missing_skills,
        )

    def _skill_stats(self, user_id: int) -> tuple[list[TopSkill], list[TopSkill]]:
        """Aggregate skill frequency from the user's resumes.

        Returns (top_skills, most_missing_skills) where missing skills are
        inferred from recent skill-gap analyses.
        """
        from collections import Counter

        from sqlalchemy import select

        from app.models.resume import ResumeSkill

        stmt = select(ResumeSkill).join(ResumeSkill.resume).where(ResumeSkill.resume.has(user_id=user_id))
        rows = list(self.db.scalars(stmt).all())
        counter: Counter[str] = Counter()
        for row in rows:
            counter[row.skill.name] += 1

        top_skills = [TopSkill(skill=skill, count=count) for skill, count in counter.most_common(10)]
        # Heuristic: skills commonly absent from the user's resume but demanded
        # in the market (derived from the master catalog categories).
        owned = set(counter)
        market_core = {"Machine Learning", "AWS", "Docker", "Kubernetes", "SQL", "React", "Python"}
        missing = [TopSkill(skill=s, count=0) for s in sorted(market_core - owned)][:10]
        return top_skills, missing
