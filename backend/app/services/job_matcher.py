"""Job matching service using sentence embeddings and skill overlap."""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.ml.embeddings import EmbeddingService, cosine_similarity
from app.repositories.job_repo import JobRepository
from app.schemas.job import JobMatchResponse, JobMatchResult, JobOut
from app.services.skill_extractor import SkillExtractor

logger = logging.getLogger("app.services.job_matcher")


class JobMatchingService:
    """Ranks jobs against a user profile or free-text query."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.jobs = JobRepository(db)
        self.embeddings = EmbeddingService()
        self.skill_extractor = SkillExtractor()

    def match(self, query: str, *, top_k: int = 10) -> JobMatchResponse:
        query_embedding = self.embeddings.encode_single(query)
        jobs, _ = self.jobs.list_public(page=1, page_size=500)

        scored: list[tuple[float, object]] = []
        for job in jobs:
            # Prefer a persisted embedding; otherwise compute lazily.
            embedding = job.embedding
            if embedding is None:
                embedding = self.embeddings.encode_single(job.description).tolist()
                job.embedding = embedding
            sim = cosine_similarity(query_embedding, embedding)
            scored.append((sim, job))
        self.db.commit()  # persist lazily-computed embeddings

        scored.sort(key=lambda x: x[0], reverse=True)
        query_skills = {s["name"] for s in self.skill_extractor.extract(query)}

        results: list[JobMatchResult] = []
        for sim, job in scored[:top_k]:
            job_skill_names = set(job.skills or [])
            if not job_skill_names and job.description:
                job_skill_names = {s["name"] for s in self.skill_extractor.extract(job.description)}
            matched = sorted(query_skills & job_skill_names)
            missing = sorted(job_skill_names - query_skills)
            results.append(
                JobMatchResult(
                    job=JobOut.model_validate(job),
                    similarity=round(float(sim), 4),
                    matched_skills=matched,
                    missing_skills=missing[:10],
                )
            )
        logger.info("job_match_completed", extra={"query_len": len(query), "results": len(results)})
        return JobMatchResponse(query=query, top_k=top_k, results=results)
