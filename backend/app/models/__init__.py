"""ORM model registry. Importing this module registers all models on Base."""

from app.db.base import Base
from app.models.audit import AuditLog
from app.models.job import Job, JobApplication
from app.models.learning import LearningResource, Recommendation
from app.models.prediction import Prediction, PredictionHistory
from app.models.resume import Resume, ResumeSkill, Skill
from app.models.user import Session, User

__all__ = [
    "AuditLog",
    "Base",
    "Job",
    "JobApplication",
    "LearningResource",
    "Prediction",
    "PredictionHistory",
    "Recommendation",
    "Resume",
    "ResumeSkill",
    "Session",
    "Skill",
    "User",
]
