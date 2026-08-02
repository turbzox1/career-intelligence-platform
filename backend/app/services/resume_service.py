"""Resume upload, parsing and skill-attribution service."""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.models.user import User
from app.repositories.resume_repo import ResumeRepository, ResumeSkillRepository, SkillRepository
from app.services.resume_parser import detect_file_type, extract_text_from_bytes, parse_resume_text
from app.services.skill_extractor import SkillExtractor
from app.services.storage import build_storage_key, get_storage

logger = logging.getLogger("app.services.resume_service")


class ResumeService:
    """Uploads, parses and persists resumes with extracted skills."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.resumes = ResumeRepository(db)
        self.skills = SkillRepository(db)
        self.resume_skills = ResumeSkillRepository(db)
        self.storage = get_storage()
        self.skill_extractor = SkillExtractor()

    def upload(self, user: User, *, filename: str, content: bytes) -> dict:
        file_type = detect_file_type(filename)
        raw_text = extract_text_from_bytes(content, filename, file_type)
        storage_key = build_storage_key(user_id=user.id, filename=filename, content=content)
        self.storage.save(storage_key, content)

        parsed = parse_resume_text(raw_text)
        resume = self.resumes.create(
            user_id=user.id,
            filename=filename,
            file_type=file_type,
            storage_key=storage_key,
            file_size_bytes=len(content),
            raw_text=raw_text,
            parse_status="parsed",
            parsed_data=parsed,
        )
        skill_names = self._persist_skills(resume.id, parsed)
        self.db.commit()
        self.db.refresh(resume)

        logger.info(
            "resume_uploaded",
            extra={"user_id": user.id, "resume_id": resume.id, "skills": len(skill_names)},
        )
        return {"resume": resume, "skills": skill_names}

    def _persist_skills(self, resume_id: int, parsed: dict) -> list[str]:
        """Extract and persist normalised skills with provenance."""
        texts = []
        texts.extend(parsed.get("skills") or [])
        texts.extend(parsed.get("technologies") or [])
        texts.append(" ".join(parsed.get("experience", []) if isinstance(parsed.get("experience"), list) else []))
        source_text = " | ".join(t for t in texts if t)

        extracted = self.skill_extractor.extract(source_text)
        names: list[str] = []
        for skill in extracted:
            record = self.skills.get_or_create(skill["name"], category=skill["category"])
            self.resume_skills.create(
                resume_id=resume_id,
                skill_id=record.id,
                source=skill["source"],
                confidence=skill["confidence"],
            )
            names.append(record.name)
        return names

    def list_for_user(self, user: User, *, page: int, page_size: int):
        return self.resumes.list_for_user(user.id, page=page, page_size=page_size)

    def get_for_user(self, user: User, resume_id: int):
        resume = self.resumes.get_for_user(resume_id, user.id)
        if resume is None:
            raise NotFoundError("Resume not found")
        return resume

    def delete(self, user: User, resume_id: int) -> None:
        resume = self.get_for_user(user, resume_id)
        if resume.storage_key and settings.storage_backend != "s3":
            try:
                self.storage.delete(resume.storage_key)
            except Exception as exc:  # pragma: no cover - best effort cleanup
                logger.warning("storage delete failed: %s", exc)
        self.resumes.delete(resume)
        self.db.commit()

    def skills_for_resume(self, resume_id: int) -> list[dict]:
        return [
            {
                "name": rs.skill.name,
                "category": rs.skill.category,
                "source": rs.source,
                "confidence": rs.confidence,
            }
            for rs in self.resume_skills.list_for_resume(resume_id)
        ]
