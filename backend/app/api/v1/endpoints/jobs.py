"""Job endpoints: listing, matching and ingestion."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import CurrentUser, DbDep, require_roles
from app.models.user import User
from app.repositories.job_repo import JobApplicationRepository, JobRepository
from app.schemas.common import Message, Page
from app.schemas.job import JobCreate, JobMatchResponse, JobOut
from app.services.job_matcher import JobMatchingService

router = APIRouter(prefix="/jobs", tags=["jobs"])

AdminUser = Annotated[User, Depends(require_roles("admin"))]


@router.get("", response_model=Page[JobOut])
def list_jobs(
    db: DbDep,
    page: int = 1,
    page_size: int = 20,
    title: str | None = Query(default=None),
    company: str | None = Query(default=None),
    location: str | None = Query(default=None),
) -> Page[JobOut]:
    """List job postings with optional filtering."""
    items, total = JobRepository(db).list_public(
        page=page, page_size=page_size, title=title, company=company, location=location
    )
    pages = (total + page_size - 1) // page_size
    return Page[JobOut](
        items=[JobOut.model_validate(j) for j in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.post("/match", response_model=JobMatchResponse)
def match_jobs(payload: dict, db: DbDep, top_k: int = 10) -> JobMatchResponse:
    """Rank jobs by similarity to a free-text query or profile summary."""
    query = str(payload.get("query", ""))
    if len(query) < 10:
        from fastapi import HTTPException

        raise HTTPException(status_code=422, detail="query must be at least 10 characters")
    return JobMatchingService(db).match(query, top_k=top_k)


@router.post("", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreate, db: DbDep, _admin: AdminUser) -> JobOut:
    """Ingest a job posting (admin only)."""
    repo = JobRepository(db)
    existing = repo.get_by_external_key(payload.external_key)
    if existing:
        return JobOut.model_validate(existing)
    job = repo.create(**payload.model_dump())
    db.commit()
    db.refresh(job)
    return JobOut.model_validate(job)


@router.post("/{job_id}/save", response_model=Message)
def save_job(job_id: int, user: CurrentUser, db: DbDep) -> Message:
    """Save a job to the current user's applications."""
    repo = JobApplicationRepository(db)
    job = JobRepository(db).get(job_id)
    if job is None:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("Job not found")
    if not repo.exists(user.id, job_id):
        repo.create(user_id=user.id, job_id=job_id, match_score=0.0, status="saved")
        db.commit()
    return Message(message="Job saved")
