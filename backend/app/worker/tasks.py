"""Celery tasks.

Contains long-running or background work such as bulk job embedding and
analytics recomputation. Salary predictions run synchronously for low
latency; heavier NLP work is dispatched here.
"""

from __future__ import annotations

import logging

from app.ml.embeddings import EmbeddingService
from app.worker.celery_app import celery_app

logger = logging.getLogger("app.worker.tasks")


@celery_app.task(name="jobs.compute_embeddings", bind=True, max_retries=3)
def compute_job_embeddings(self, job_ids: list[int]) -> int:
    """Compute and persist sentence embeddings for a batch of jobs."""
    from sqlalchemy import select

    from app.db.session import SessionLocal
    from app.models.job import Job

    embeddings = EmbeddingService()
    processed = 0
    with SessionLocal() as db:
        stmt = select(Job).where(Job.id.in_(job_ids))
        for job in db.scalars(stmt).all():
            try:
                job.embedding = embeddings.encode_single(job.description).tolist()
                processed += 1
            except Exception as exc:  # pragma: no cover
                logger.warning("embedding failed for job %s: %s", job.id, exc)
        db.commit()
    logger.info("job_embeddings_computed", extra={"count": processed})
    return processed


@celery_app.task(name="jobs.embed_all", bind=True, max_retries=3)
def embed_all_jobs(self) -> int:
    """Compute embeddings for every job that lacks one."""
    from sqlalchemy import select

    from app.db.session import SessionLocal
    from app.models.job import Job

    with SessionLocal() as db:
        job_ids = [
            int(job_id) for job_id in db.scalars(select(Job.id).where(Job.embedding.is_(None)).limit(10000)).all()
        ]
    return compute_job_embeddings.delay(job_ids).get() if job_ids else 0
