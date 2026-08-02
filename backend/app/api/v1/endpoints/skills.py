"""Skill endpoints: skill-gap analysis, skill catalog and recommendations."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbDep
from app.data.skills_master import all_skills
from app.repositories.resume_repo import SkillRepository
from app.schemas.learning import LearningRoadmapRequest, LearningRoadmapResponse
from app.schemas.skill import SkillGapRequest, SkillGapResponse, SkillOut
from app.services.learning_service import LearningService
from app.services.skill_gap_service import SkillGapService

router = APIRouter(prefix="/skills", tags=["skills"])


@router.post("/gap", response_model=SkillGapResponse)
def skill_gap(payload: SkillGapRequest, db: DbDep) -> SkillGapResponse:
    """Analyse the gap between resume skills and a job description."""
    return SkillGapService(db).analyze(resume_skills=payload.resume_skills, job_description=payload.job_description)


@router.get("/catalog", response_model=list[SkillOut])
def skill_catalog(db: DbDep, query: str = "", limit: int = 100) -> list[SkillOut]:
    """List or search the master skill catalog."""
    repo = SkillRepository(db)
    if query:
        return [SkillOut.model_validate(s) for s in repo.search(query, limit=limit)]
    return [SkillOut(id=0, **s) for s in all_skills()][:limit]


@router.post("/recommendations/roadmap", response_model=LearningRoadmapResponse)
def learning_roadmap(payload: LearningRoadmapRequest, db: DbDep) -> LearningRoadmapResponse:
    """Build a personalised learning roadmap for a set of missing skills."""
    return LearningService(db).build_roadmap(payload.missing_skills, payload.daily_hours)


@router.post("/recommendations", response_model=list)
def generate_recommendations(payload: SkillGapRequest, user: CurrentUser, db: DbDep) -> list:
    """Generate and persist learning recommendations for missing skills."""
    gap = SkillGapService(db).analyze(resume_skills=payload.resume_skills, job_description=payload.job_description)
    missing = [item.model_dump() for item in gap.missing_skills]
    return LearningService(db).recommend_for_missing_skills(user, missing)


@router.get("/recommendations", response_model=list)
def list_recommendations(user: CurrentUser, db: DbDep, limit: int = 50) -> list:
    """List the current user's persisted learning recommendations."""
    return LearningService(db).list_recommendations(user, limit=limit)
