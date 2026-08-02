"""Versioned API router aggregation."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import analytics, auth, health, jobs, predictions, resumes, skills, users

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(resumes.router)
api_router.include_router(predictions.router)
api_router.include_router(skills.router)
api_router.include_router(jobs.router)
api_router.include_router(analytics.router)
