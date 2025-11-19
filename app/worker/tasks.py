"""
Celery tasks module.

Defines async tasks for background processing of summary generation.
"""
import logging
import time
from contextlib import contextmanager
from app.worker.celery_app import celery_app
from app.db.session import SessionLocal
from app.services.summary_service import SummaryService
from app.schemas.summary import SummaryOptions
from app.core.settings import settings
from app.core.metrics import (
    CELERY_TASKS_TOTAL,
    CELERY_TASK_DURATION_SECONDS,
    SUMMARY_REQUESTS_TOTAL,
    SUMMARY_GENERATION_DURATION_SECONDS,
    SUMMARY_GENERATION_ERRORS_TOTAL
)

logger = logging.getLogger(__name__)


@contextmanager
def get_db_session():
    """
    Context manager for database session.

    Ensures proper cleanup of database connections.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@celery_app.task(bind=True, name="generate_summary_task")
def generate_summary_task(
    self,
    patient_id: int,
    audience: str = "clinician",
    max_length: int = 500
) -> dict:
    """
    Async task to generate patient summary.

    Runs in background worker to keep API responsive.

    Parameters:
        patient_id: The patient's unique identifier
        audience: Target audience for the summary
        max_length: Maximum length of summary in characters

    Returns:
        Dictionary containing summary data or error message
    """
    logger.info(f"Starting summary generation for patient {patient_id}")
    start_time = time.time()

    # Record task started metric
    if settings.METRICS_ENABLED:
        CELERY_TASKS_TOTAL.labels(task_name="generate_summary", status="started").inc()
        SUMMARY_REQUESTS_TOTAL.labels(audience=audience, mode="async").inc()

    try:
        with get_db_session() as db:
            service = SummaryService(db)
            options = SummaryOptions(audience=audience, max_length=max_length)
            result = service.generate_patient_summary(patient_id, options)

            if result is None:
                if settings.METRICS_ENABLED:
                    CELERY_TASKS_TOTAL.labels(task_name="generate_summary", status="failed").inc()
                return {
                    "status": "error",
                    "error": "Patient not found",
                    "error_code": "PATIENT_NOT_FOUND"
                }

            # Record success metrics
            duration = time.time() - start_time
            if settings.METRICS_ENABLED:
                CELERY_TASKS_TOTAL.labels(task_name="generate_summary", status="succeeded").inc()
                CELERY_TASK_DURATION_SECONDS.labels(task_name="generate_summary").observe(duration)
                SUMMARY_GENERATION_DURATION_SECONDS.labels(provider=settings.LLM_PROVIDER).observe(duration)

            return {
                "status": "completed",
                "heading": {
                    "name": result.heading.name,
                    "age": result.heading.age,
                    "mrn": result.heading.mrn
                },
                "summary": result.summary,
                "note_count": result.note_count
            }

    except Exception as e:
        logger.error(f"Summary generation failed: {e}", exc_info=True)

        # Record error metrics
        if settings.METRICS_ENABLED:
            CELERY_TASKS_TOTAL.labels(task_name="generate_summary", status="failed").inc()
            SUMMARY_GENERATION_ERRORS_TOTAL.labels(
                provider=settings.LLM_PROVIDER,
                error_type=type(e).__name__
            ).inc()

        return {
            "status": "error",
            "error": str(e),
            "error_code": "GENERATION_FAILED"
        }
