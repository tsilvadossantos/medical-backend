"""
Job schema module.

Defines Pydantic models for async job tracking.
"""
from typing import Optional, Any
from pydantic import BaseModel


class JobResponse(BaseModel):
    """
    Schema for async job creation response.

    Contains job ID for status polling.
    """
    job_id: str
    status: str
    message: str


class JobStatusResponse(BaseModel):
    """
    Schema for job status response.

    Contains current status and result when completed.
    """
    job_id: str
    status: str
    result: Optional[Any] = None
