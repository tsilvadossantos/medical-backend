"""
Metrics endpoint module.

Exposes Prometheus metrics for scraping.
"""
from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.core.settings import settings

router = APIRouter()


@router.get("/metrics")
def get_metrics():
    """
    Expose Prometheus metrics.

    Returns metrics in Prometheus text format for scraping.

    Returns:
        Prometheus metrics in text format
    """
    if not settings.METRICS_ENABLED:
        return Response(
            content="Metrics disabled",
            status_code=404
        )

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
