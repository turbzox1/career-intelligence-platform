"""Job matching schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class JobOut(BaseModel):
    """Public job representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company: str
    location: str
    salary_min: float | None
    salary_max: float | None
    currency: str
    source_url: str
    created_at: datetime


class JobMatchResult(BaseModel):
    """A single matched job with a similarity score."""

    job: JobOut
    similarity: float = Field(ge=0, le=1)
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)


class JobMatchResponse(BaseModel):
    """Ranked list of matching jobs."""

    query: str
    top_k: int
    results: list[JobMatchResult] = Field(default_factory=list)


class JobCreate(BaseModel):
    """Admin payload for ingesting a job posting."""

    external_key: str
    title: str = Field(min_length=1)
    company: str = Field(min_length=1)
    location: str = ""
    description: str = Field(min_length=10)
    salary_min: float | None = None
    salary_max: float | None = None
    currency: str = "USD"
    source_url: str = ""
