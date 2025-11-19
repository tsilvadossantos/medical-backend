"""
Celery application configuration.

Configures Celery for async task processing with Redis as broker and backend.
"""
from celery import Celery
from app.core.settings import settings

celery_app = Celery(
    "medical_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.worker.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    result_expires=3600,
)
