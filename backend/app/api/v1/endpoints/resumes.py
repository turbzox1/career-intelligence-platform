"""Resume endpoints: upload, list, retrieve, delete."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, File, UploadFile, status

from app.api.deps import CurrentUser, DbDep
from app.schemas.common import Message, Page
from app.schemas.resume import ResumeListItem, ResumeOut, ResumeUploadResponse
from app.services.resume_service import ResumeService

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("/upload", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: Annotated[UploadFile, File(...)],
    user: CurrentUser,
    db: DbDep,
) -> ResumeUploadResponse:
    """Upload and parse a resume (PDF, DOCX or TXT)."""
    content = await file.read()
    result = ResumeService(db).upload(user, filename=file.filename or "resume.txt", content=content)
    return ResumeUploadResponse(resume=result["resume"], skills=result["skills"])


@router.get("", response_model=Page[ResumeListItem])
def list_resumes(
    user: CurrentUser,
    db: DbDep,
    page: int = 1,
    page_size: int = 20,
) -> Page[ResumeListItem]:
    """List the current user's uploaded resumes."""
    items, total = ResumeService(db).list_for_user(user, page=page, page_size=page_size)
    pages = (total + page_size - 1) // page_size
    return Page[ResumeListItem](
        items=[ResumeListItem.model_validate(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/{resume_id}", response_model=ResumeOut)
def get_resume(resume_id: int, user: CurrentUser, db: DbDep) -> ResumeOut:
    """Retrieve a single parsed resume."""
    return ResumeOut.model_validate(ResumeService(db).get_for_user(user, resume_id))


@router.delete("/{resume_id}", response_model=Message)
def delete_resume(resume_id: int, user: CurrentUser, db: DbDep) -> Message:
    """Delete a resume and its extracted skills."""
    ResumeService(db).delete(user, resume_id)
    return Message(message="Resume deleted")
