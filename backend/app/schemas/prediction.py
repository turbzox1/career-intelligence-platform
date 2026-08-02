"""Salary prediction schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

VALID_LOCATIONS = {
    "remote",
    "san_francisco",
    "new_york",
    "seattle",
    "austin",
    "london",
    "bengaluru",
    "berlin",
    "toronto",
    "singapore",
}
VALID_INDUSTRIES = {
    "technology",
    "finance",
    "healthcare",
    "retail",
    "manufacturing",
    "consulting",
    "education",
    "media",
    "energy",
}


class SalaryPredictionRequest(BaseModel):
    """Feature inputs for a salary prediction."""

    years_experience: float = Field(ge=0, le=60)
    degree_level: str = Field(default="bachelor", pattern="^(none|associate|bachelor|master|phd)$")
    location: str = Field(default="remote", min_length=1)
    industry: str = Field(default="technology", min_length=1)
    company_size: str = Field(default="mid", pattern="^(startup|small|mid|large|enterprise)$")
    title: str = Field(default="software_engineer", min_length=1)
    skills: list[str] = Field(default_factory=list)
    resume_id: int | None = None

    @field_validator("location")
    @classmethod
    def _location(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("industry")
    @classmethod
    def _industry(cls, value: str) -> str:
        return value.strip().lower()


class FeatureContribution(BaseModel):
    """One SHAP contribution entry."""

    feature: str
    value: float
    contribution: float


class ExplanationOut(BaseModel):
    """Explainability payload for a prediction."""

    base_value: float
    predicted_value: float
    features: list[FeatureContribution]
    waterfall: list[FeatureContribution] = Field(default_factory=list)


class SalaryPredictionResponse(BaseModel):
    """Complete salary prediction output."""

    model_config = ConfigDict(from_attributes=True)

    prediction_id: int
    predicted_salary: float
    currency: str = "USD"
    lower_bound: float | None
    upper_bound: float | None
    confidence: float | None
    model_name: str
    model_version: str
    explanation: ExplanationOut | None = None
    input_features: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class PredictionHistoryItem(BaseModel):
    """A prediction row for history/dashboard views."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    predicted_salary: float
    lower_bound: float | None
    upper_bound: float | None
    model_name: str
    created_at: datetime
