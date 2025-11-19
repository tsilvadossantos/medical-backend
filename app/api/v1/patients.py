"""
Patient endpoints module.

Provides CRUD endpoints for patient management.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.services.patient_service import PatientService
from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientListResponse
)

router = APIRouter(prefix="/patients", tags=["patients"])

# Valid fields for sorting
VALID_SORT_FIELDS = {"id", "name", "date_of_birth", "created_at", "updated_at"}
VALID_SORT_ORDERS = {"asc", "desc"}


@router.get("", response_model=PatientListResponse)
def list_patients(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("id", description="Field to sort by (id, name, date_of_birth, created_at, updated_at)"),
    sort_order: str = Query("asc", description="Sort direction (asc/desc)"),
    search: Optional[str] = Query(None, max_length=100, description="Search term for name"),
    db: Session = Depends(get_db)
):
    """
    List all patients with pagination.

    Supports sorting by any field and optional fuzzy search by name.

    Parameters:
        page: Page number (1-indexed)
        size: Number of items per page
        sort_by: Field to sort by
        sort_order: Sort direction
        search: Optional search term

    Returns:
        Paginated list of patients
    """
    # Validate sort_by parameter
    if sort_by not in VALID_SORT_FIELDS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by field. Must be one of: {', '.join(sorted(VALID_SORT_FIELDS))}"
        )

    # Validate sort_order parameter
    if sort_order.lower() not in VALID_SORT_ORDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_order. Must be one of: {', '.join(VALID_SORT_ORDERS)}"
        )

    service = PatientService(db)
    return service.get_patients(
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order.lower(),
        search=search
    )


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """
    Get a specific patient by ID.

    Parameters:
        patient_id: The patient's unique identifier

    Returns:
        Patient data

    Raises:
        HTTPException: 404 if patient not found
    """
    service = PatientService(db)
    patient = service.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.post("", response_model=PatientResponse, status_code=201)
def create_patient(patient_data: PatientCreate, db: Session = Depends(get_db)):
    """
    Create a new patient.

    Parameters:
        patient_data: Patient data for creation

    Returns:
        Newly created patient
    """
    service = PatientService(db)
    return service.create_patient(patient_data)


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing patient.

    Parameters:
        patient_id: The patient's unique identifier
        patient_data: Updated patient data

    Returns:
        Updated patient

    Raises:
        HTTPException: 404 if patient not found
    """
    service = PatientService(db)
    patient = service.update_patient(patient_id, patient_data)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.delete("/{patient_id}", status_code=204)
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """
    Delete a patient.

    Parameters:
        patient_id: The patient's unique identifier

    Raises:
        HTTPException: 404 if patient not found
    """
    service = PatientService(db)
    if not service.delete_patient(patient_id):
        raise HTTPException(status_code=404, detail="Patient not found")
