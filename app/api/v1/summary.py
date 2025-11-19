"""
Summary endpoints module.

Provides endpoints for generating patient summaries synchronously and asynchronously.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from celery.result import AsyncResult
from app.api.dependencies import get_db
from app.services.summary_service import SummaryService
from app.schemas.summary import SummaryResponse, SummaryOptions
from app.schemas.job import JobResponse, JobStatusResponse
from app.worker.tasks import generate_summary_task
from app.repositories.patient_repository import PatientRepository

router = APIRouter(prefix="/patients/{patient_id}/summary", tags=["summary"])


@router.get("", response_model=SummaryResponse)
def get_patient_summary(
    patient_id: int,
    audience: str = Query("clinician", description="Target audience (clinician/family)"),
    max_length: int = Query(500, ge=100, le=2000, description="Maximum summary length"),
    db: Session = Depends(get_db)
):
    """
    Generate a summary for a patient synchronously.

    Synthesizes patient profile and notes into a coherent narrative
    tailored to the specified audience.

    Parameters:
        patient_id: The patient's unique identifier
        audience: Target audience for the summary
        max_length: Maximum length of the summary in characters

    Returns:
        Generated patient summary

    Raises:
        HTTPException: 404 if patient not found
    """
    service = SummaryService(db)
    options = SummaryOptions(audience=audience, max_length=max_length)
    summary = service.generate_patient_summary(patient_id, options)

    if summary is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    return summary


@router.post("/async", response_model=JobResponse, status_code=202)
def create_summary_job(
    patient_id: int,
    audience: str = Query("clinician", description="Target audience (clinician/family)"),
    max_length: int = Query(500, ge=100, le=2000, description="Maximum summary length"),
    db: Session = Depends(get_db)
):
    """
    Queue a summary generation job for async processing.

    Returns immediately with a job ID that can be used to poll for results.

    Parameters:
        patient_id: The patient's unique identifier
        audience: Target audience for the summary
        max_length: Maximum length of the summary in characters

    Returns:
        Job ID and status

    Raises:
        HTTPException: 404 if patient not found
    """
    repo = PatientRepository(db)
    if not repo.get_by_id(patient_id):
        raise HTTPException(status_code=404, detail="Patient not found")

    task = generate_summary_task.delay(patient_id, audience, max_length)

    return JobResponse(
        job_id=task.id,
        status="queued",
        message=f"Summary generation queued for patient {patient_id}"
    )


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job_status(patient_id: int, job_id: str):
    """
    Get the status of an async summary generation job.

    Parameters:
        patient_id: The patient's unique identifier
        job_id: The job's unique identifier

    Returns:
        Job status and result if completed
    """
    result = AsyncResult(job_id)

    status_map = {
        "PENDING": "pending",
        "STARTED": "processing",
        "SUCCESS": "completed",
        "FAILURE": "failed",
        "REVOKED": "cancelled"
    }

    status = status_map.get(result.status, result.status.lower())

    response = JobStatusResponse(
        job_id=job_id,
        status=status,
        result=None
    )

    if result.ready():
        response.result = result.result

    return response
