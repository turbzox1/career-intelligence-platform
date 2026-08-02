"""Job persistence operations."""

from __future__ import annotations

from sqlalchemy import func, select

from app.models.job import Job, JobApplication
from app.repositories.base import BaseRepository


class JobRepository(BaseRepository[Job]):
    """Data access for job postings."""

    _model = Job

    def get_by_external_key(self, external_key: str) -> Job | None:
        stmt = select(Job).where(Job.external_key == external_key)
        return self.db.scalar(stmt)

    def list_public(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        title: str | None = None,
        company: str | None = None,
        location: str | None = None,
    ) -> tuple[list[Job], int]:
        stmt = select(Job)
        if title:
            stmt = stmt.where(Job.title.ilike(f"%{title}%"))
        if company:
            stmt = stmt.where(Job.company.ilike(f"%{company}%"))
        if location:
            stmt = stmt.where(Job.location.ilike(f"%{location}%"))
        total = self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        stmt = stmt.order_by(Job.id.desc()).offset((page - 1) * page_size).limit(page_size)
        return list(self.db.scalars(stmt).all()), total


class JobApplicationRepository(BaseRepository[JobApplication]):
    """Data access for job applications."""

    _model = JobApplication

    def exists(self, user_id: int, job_id: int) -> bool:
        stmt = select(JobApplication).where(JobApplication.user_id == user_id, JobApplication.job_id == job_id)
        return self.db.scalar(stmt) is not None
