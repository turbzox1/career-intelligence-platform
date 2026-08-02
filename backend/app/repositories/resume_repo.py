"""Resume and skill persistence operations."""

from __future__ import annotations

from sqlalchemy import select

from app.models.resume import Resume, ResumeSkill, Skill
from app.repositories.base import BaseRepository


class ResumeRepository(BaseRepository[Resume]):
    """Data access for resumes."""

    _model = Resume

    def list_for_user(self, user_id: int, *, page: int = 1, page_size: int = 20) -> tuple[list[Resume], int]:
        filters = {"user_id": user_id}
        return self.list(page=page, page_size=page_size, filters=filters, order_by="id.desc()")

    def get_for_user(self, resume_id: int, user_id: int) -> Resume | None:
        stmt = select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id)
        return self.db.scalar(stmt)


class SkillRepository(BaseRepository[Skill]):
    """Data access for the master skills catalog."""

    _model = Skill

    def get_by_name(self, name: str) -> Skill | None:
        stmt = select(Skill).where(Skill.name == name)
        return self.db.scalar(stmt)

    def get_or_create(self, name: str, category: str = "general") -> Skill:
        skill = self.get_by_name(name)
        if skill is None:
            skill = self.create(name=name, category=category)
        return skill

    def search(self, query: str, *, limit: int = 50) -> list[Skill]:
        pattern = f"%{query}%"
        stmt = select(Skill).where(Skill.name.ilike(pattern)).limit(limit)
        return list(self.db.scalars(stmt).all())


class ResumeSkillRepository(BaseRepository[ResumeSkill]):
    """Data access for the resume<->skill join table."""

    _model = ResumeSkill

    def list_for_resume(self, resume_id: int) -> list[ResumeSkill]:
        stmt = select(ResumeSkill).where(ResumeSkill.resume_id == resume_id)
        return list(self.db.scalars(stmt).all())

    def delete_for_resume(self, resume_id: int) -> None:
        from sqlalchemy import delete

        self.db.execute(delete(ResumeSkill).where(ResumeSkill.resume_id == resume_id))
