"""Resume, Skill and ResumeSkill ORM models."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Resume(TimestampMixin, Base):
    """An uploaded resume document and its parsed content."""

    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(16), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    raw_text: Mapped[str] = mapped_column(Text, default="", nullable=False)
    parse_status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Parsed structured content extracted by the NLP pipeline.
    parsed_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    user: Mapped[User] = relationship(back_populates="resumes")
    skills: Mapped[list[ResumeSkill]] = relationship(back_populates="resume", cascade="all, delete-orphan")


class Skill(TimestampMixin, Base):
    """Normalised master skill catalog (single source of truth)."""

    __tablename__ = "skills"
    __table_args__ = (UniqueConstraint("name", name="uq_skills_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(80), index=True, default="general")
    # Aliases used during skill normalisation, e.g. {"Python3", "PYTHON"}.
    aliases: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    resume_skills: Mapped[list[ResumeSkill]] = relationship(back_populates="skill")


class ResumeSkill(TimestampMixin, Base):
    """Join table linking a resume to a normalised skill with provenance."""

    __tablename__ = "resume_skills"
    __table_args__ = (UniqueConstraint("resume_id", "skill_id", name="uq_resume_skills_pair"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id", ondelete="CASCADE"), index=True, nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), index=True, nullable=False)
    source: Mapped[str] = mapped_column(String(32), default="rule", nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    resume: Mapped[Resume] = relationship(back_populates="skills")
    skill: Mapped[Skill] = relationship(back_populates="resume_skills")
