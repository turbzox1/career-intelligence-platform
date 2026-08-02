"""Shared/common Pydantic schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Message(BaseModel):
    """A generic message response."""

    message: str


class Page[ItemT](BaseModel):
    """Generic paginated response envelope."""

    items: list[ItemT]
    total: int
    page: int
    page_size: int
    pages: int


class PaginationParams(BaseModel):
    """Query parameters for pagination."""

    page: int = Field(default=1, ge=1, le=10000)
    page_size: int = Field(default=20, ge=1, le=100)
