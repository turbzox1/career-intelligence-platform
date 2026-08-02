"""Resume and parsed-content schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ParsedResumeData(BaseModel):
    """Structured content extracted from a resume by the NLP pipeline."""

    name: str | None = None
    email: str | None = None
    phone: str | None = None
    summary: str | None = None
    experience: list[dict[str, Any]] = Field(default_factory=list)
    education: list[dict[str, Any]] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    years_of_experience: float = 0.0


class ResumeOut(BaseModel):
    """Public resume representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    file_type: str
    file_size_bytes: int
    parse_status: str
    error_message: str | None
    parsed_data: dict[str, Any]
    created_at: datetime


class ResumeUploadResponse(BaseModel):
    """Response returned after a resume upload."""

    resume: ResumeOut
    skills: list[str] = Field(default_factory=list)


class ResumeListItem(BaseModel):
    """A resume row in list views."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    file_type: str
    file_size_bytes: int
    parse_status: str
    created_at: datetime
