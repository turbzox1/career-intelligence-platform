"""Analytics dashboard schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class TrendPoint(BaseModel):
    """A single point on a time-series chart."""

    date: str
    value: float


class SalaryByGroup(BaseModel):
    """Average salary grouped by a categorical feature."""

    label: str
    average_salary: float
    count: int


class TopSkill(BaseModel):
    """A skill with occurrence frequency."""

    skill: str
    count: int


class AnalyticsResponse(BaseModel):
    """Aggregated analytics payload for the dashboard."""

    total_predictions: int
    average_salary: float
    salary_trend: list[TrendPoint]
    salary_by_location: list[SalaryByGroup]
    salary_by_industry: list[SalaryByGroup]
    salary_by_experience: list[TrendPoint]
    top_skills: list[TopSkill]
    most_missing_skills: list[TopSkill]
    raw: dict[str, Any] = {}
