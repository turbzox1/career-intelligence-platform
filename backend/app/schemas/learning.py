"""Learning recommendation schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class LearningResourceOut(BaseModel):
    """A learning resource representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    skill_name: str
    title: str
    provider: str
    url: str
    resource_type: str
    difficulty: str
    estimated_hours: float
    rating: float | None


class RecommendationOut(BaseModel):
    """A learning recommendation with rationale."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    skill_name: str
    reason: str
    score: float
    status: str
    priority: int
    resource: LearningResourceOut


class LearningRoadmapRequest(BaseModel):
    """Input for building a personalised learning roadmap."""

    missing_skills: list[str] = Field(min_length=1, max_length=30)
    daily_hours: float = Field(default=1.0, ge=0.25, le=12)


class RoadmapStep(BaseModel):
    """A single step in a learning roadmap."""

    skill: str
    priority: int
    estimated_hours: float
    resources: list[LearningResourceOut] = Field(default_factory=list)


class LearningRoadmapResponse(BaseModel):
    """A complete personalised learning roadmap."""

    total_estimated_hours: float
    estimated_weeks: float
    steps: list[RoadmapStep] = Field(default_factory=list)
