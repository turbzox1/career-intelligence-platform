"""Celery application for asynchronous jobs."""

from __future__ import annotations

import logging

from celery import Celery
from celery.signals import after_setup_logger

from app.core.config import settings

logger = logging.getLogger("app.worker")

celery_app = Celery(
    "career_intelligence",
    broker=settings.resolved_celery_broker_url,
    backend=settings.resolved_celery_result_backend,
    include=["app.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,
    task_soft_time_limit=540,
    worker_max_tasks_per_child=50,
    broker_connection_retry_on_startup=True,
)


@after_setup_logger.connect
def _setup_celery_logger(logger, **kwargs):  # noqa: ANN001
    logger.setLevel(logging.INFO)
