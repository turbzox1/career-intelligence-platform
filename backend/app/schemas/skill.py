"""Skill-related schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SkillOut(BaseModel):
    """A normalised skill from the master catalog."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    weight: float


class ResumeSkillOut(BaseModel):
    """A skill detected on a resume with provenance."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    source: str
    confidence: float
    skill: SkillOut


class SkillGapRequest(BaseModel):
    """Skill-gap analysis inputs."""

    resume_skills: list[str] = Field(default_factory=list)
    job_description: str = Field(min_length=10)


class MissingSkill(BaseModel):
    """A single missing skill with priority."""

    skill: str
    category: str
    priority_score: float = Field(ge=0, le=1)
    importance: str = Field(default="medium")


class SkillGapResponse(BaseModel):
    """Full skill-gap analysis output."""

    skill_match_percentage: float = Field(ge=0, le=100)
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[MissingSkill] = Field(default_factory=list)
    recommendation_priority: str = Field(default="low")
