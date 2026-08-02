"""Skill-gap analysis service."""

from __future__ import annotations

import logging
from collections import Counter

from sqlalchemy.orm import Session

from app.schemas.skill import MissingSkill, SkillGapResponse
from app.services.skill_extractor import SkillExtractor

logger = logging.getLogger("app.services.skill_gap")


class SkillGapService:
    """Compares resume skills against job-description skills."""

    def __init__(self, db: Session | None = None) -> None:
        self.db = db
        self.skill_extractor = SkillExtractor()

    def analyze(self, resume_skills: list[str], job_description: str) -> SkillGapResponse:
        normalized_resume = {self._norm(s) for s in resume_skills}
        job_skills = self._extract_job_skills(job_description)

        matched = [s for s in job_skills if self._norm(s) in normalized_resume]
        missing = [s for s in job_skills if self._norm(s) not in normalized_resume]

        match_pct = round((len(matched) / len(job_skills)) * 100, 1) if job_skills else 100.0
        missing_items = [
            MissingSkill(
                skill=skill,
                category=self._category(skill),
                priority_score=round(priority, 3),
                importance=self._importance(priority),
            )
            for skill, priority in self._prioritize(missing)
        ]
        priority = self._overall_priority(match_pct, len(missing_items))

        logger.info(
            "skill_gap_analyzed",
            extra={"matched": len(matched), "missing": len(missing_items), "match_pct": match_pct},
        )
        return SkillGapResponse(
            skill_match_percentage=match_pct,
            matched_skills=matched,
            missing_skills=missing_items,
            recommendation_priority=priority,
        )

    def _extract_job_skills(self, job_description: str) -> list[str]:
        """Extract and rank skills mentioned in a job description."""
        extracted = self.skill_extractor.extract(job_description)
        counts = Counter(e["name"] for e in extracted)
        # Order by mention frequency then alphabetically.
        return [name for name, _ in counts.most_common()]

    def _prioritize(self, skills: list[str]) -> list[tuple[str, float]]:
        """Assign a priority score to each missing skill.

        Scores are based on the skill's market weight and position in the
        job description; skills listed earlier are treated as more important.
        """
        total = len(skills) or 1
        results = []
        for idx, skill in enumerate(skills):
            base = 1.0 - (idx / total)
            weight = self._weight(skill)
            results.append((skill, min(base * 0.7 + weight * 0.3, 1.0)))
        return results

    @staticmethod
    def _weight(skill: str) -> float:
        try:
            from career_ml.features import SKILL_SALARY_DELTA

            return min(SKILL_SALARY_DELTA.get(skill, 0.5) / 12000.0, 1.0)
        except ImportError:  # pragma: no cover
            return 0.5

    @staticmethod
    def _category(skill: str) -> str:
        from app.data.skills_master import get_canonical_skill

        entry = get_canonical_skill(skill)
        return entry["category"] if entry else "general"

    @staticmethod
    def _norm(skill: str) -> str:
        return " ".join(skill.strip().lower().split())

    @staticmethod
    def _importance(priority: float) -> str:
        if priority >= 0.7:
            return "high"
        if priority >= 0.4:
            return "medium"
        return "low"

    @staticmethod
    def _overall_priority(match_pct: float, missing_count: int) -> str:
        if missing_count == 0 or match_pct >= 90:
            return "low"
        if match_pct >= 60:
            return "medium"
        return "high"
