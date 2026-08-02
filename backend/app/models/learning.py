"""Learning resources and recommendations ORM models."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import JSON, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.skill import Skill  # noqa: F401
    from app.models.user import User


class LearningResource(TimestampMixin, Base):
    """A curated learning resource (course, video, doc, roadmap)."""

    __tablename__ = "learning_resources"
    __table_args__ = (UniqueConstraint("url", name="uq_learning_resource_url"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    skill_id: Mapped[int | None] = mapped_column(
        ForeignKey("skills.id", ondelete="SET NULL"), index=True, nullable=True
    )
    skill_name: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    resource_type: Mapped[str] = mapped_column(String(32), default="course", nullable=False)
    difficulty: Mapped[str] = mapped_column(String(16), default="beginner", nullable=False)
    estimated_hours: Mapped[float] = mapped_column(Float, default=4.0, nullable=False)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    tags: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    skill: Mapped[Skill] = relationship()


class Recommendation(TimestampMixin, Base):
    """A learning recommendation generated for a user."""

    __tablename__ = "recommendations"
    __table_args__ = (UniqueConstraint("user_id", "resource_id", name="uq_recommendation_pair"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    resource_id: Mapped[int] = mapped_column(ForeignKey("learning_resources.id", ondelete="CASCADE"), nullable=False)
    skill_name: Mapped[str] = mapped_column(String(120), nullable=False)
    reason: Mapped[str] = mapped_column(Text, default="", nullable=False)
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="recommended", nullable=False)
    priority: Mapped[int] = mapped_column(default=100, nullable=False)

    user: Mapped[User] = relationship(back_populates="recommendations")
    resource: Mapped[LearningResource] = relationship()
