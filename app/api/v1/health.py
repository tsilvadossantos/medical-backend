"""
Health check endpoint module.

Provides health check endpoint for monitoring application status.
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    """
    Check application health status.

    Returns:
        JSON object with status indicator
    """
    return {"status": "ok"}
