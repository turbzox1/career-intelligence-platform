"""Structured logging configuration using stdlib logging with JSON formatter.

Logging is configured with a JSON formatter in production and a readable
formatter in development. Request context (request id, user id, path) is
attached via a contextvar so that async code can correlate log records.
"""

from __future__ import annotations

import json
import logging
import sys
import time
import uuid
from contextvars import ContextVar
from typing import Any

from app.core.config import settings

# Contextvar that holds the current request correlation metadata.
request_context: ContextVar[dict[str, Any] | None] = ContextVar("request_context", default=None)


class JsonFormatter(logging.Formatter):
    """Structured JSON log formatter for machine-parseable output."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        # Attach request context if present.
        context = request_context.get()
        if context:
            payload.update(context)
        if hasattr(record, "extra_fields") and isinstance(record.extra_fields, dict):
            payload.update(record.extra_fields)
        return json.dumps(payload, default=str)


def _build_formatter() -> logging.Formatter:
    if settings.environment == "production":
        return JsonFormatter()
    return logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")


def configure_logging() -> None:
    """Configure the root logger once for the whole process."""
    root = logging.getLogger()
    if root.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_build_formatter())
    root.addHandler(handler)
    root.setLevel(logging.INFO if not settings.debug else logging.DEBUG)

    # Keep uvicorn/access logs on a quieter level unless debugging.
    logging.getLogger("uvicorn.access").setLevel(logging.INFO if not settings.debug else logging.DEBUG)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def start_request_context(*, request_id: str | None = None, user_id: str | None = None) -> str:
    """Start a new request context and return its request id."""
    rid = request_id or uuid.uuid4().hex
    ctx = {"request_id": rid}
    if user_id:
        ctx["user_id"] = user_id
    request_context.set(ctx)
    return rid


def set_request_context(**fields: Any) -> None:
    """Merge additional fields into the current request context."""
    current = request_context.get() or {}
    request_context.set({**current, **fields})


class TimedLogger:
    """Context manager that logs the duration of a block.

    Example:
        with TimedLogger(log, "predict", stage="model_inference"):
            result = model.predict(x)
    """

    def __init__(self, logger: logging.Logger, operation: str, **meta: Any) -> None:
        self.logger = logger
        self.operation = operation
        self.meta = meta
        self._start = 0.0

    def __enter__(self) -> TimedLogger:
        self._start = time.perf_counter()
        self.logger.info("operation_start", extra={"operation": self.operation, **self.meta})
        return self

    def __exit__(self, *_: Any) -> None:
        elapsed_ms = (time.perf_counter() - self._start) * 1000
        self.logger.info(
            "operation_end",
            extra={
                "operation": self.operation,
                "duration_ms": round(elapsed_ms, 3),
                **self.meta,
            },
        )


configure_logging()
