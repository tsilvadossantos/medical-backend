"""
Patient service module.

Provides business logic for patient operations.
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.patient_repository import PatientRepository
from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientListResponse
)
from app.core.settings import settings
from app.core.metrics import (
    PATIENTS_CREATED_TOTAL,
    PATIENTS_UPDATED_TOTAL,
    PATIENTS_DELETED_TOTAL,
    PATIENTS_TOTAL
)
import math


class PatientService:
    """
    Service class for patient business logic.

    Coordinates between API layer and repository layer,
    applying business rules and transformations.
    """

    def __init__(self, db: Session):
        """
        Initialize service with database session.

        Parameters:
            db: SQLAlchemy database session
        """
        self.repository = PatientRepository(db)

    def get_patients(
        self,
        page: int = 1,
        size: int = 10,
        sort_by: str = "id",
        sort_order: str = "asc",
        search: Optional[str] = None
    ) -> PatientListResponse:
        """
        Get paginated list of patients.

        Parameters:
            page: Page number (1-indexed)
            size: Number of items per page
            sort_by: Field to sort by
            sort_order: Sort direction (asc or desc)
            search: Optional search term

        Returns:
            PatientListResponse with paginated patient data
        """
        skip = (page - 1) * size
        patients, total = self.repository.get_all(
            skip=skip,
            limit=size,
            sort_by=sort_by,
            sort_order=sort_order,
            search=search
        )

        # Update total patients gauge
        if settings.METRICS_ENABLED:
            PATIENTS_TOTAL.set(total)

        return PatientListResponse(
            items=[PatientResponse.model_validate(p) for p in patients],
            total=total,
            page=page,
            size=size,
            pages=math.ceil(total / size) if total > 0 else 0
        )

    def get_patient(self, patient_id: int) -> Optional[PatientResponse]:
        """
        Get a single patient by ID.

        Parameters:
            patient_id: The patient's unique identifier

        Returns:
            PatientResponse if found, None otherwise
        """
        patient = self.repository.get_by_id(patient_id)
        if not patient:
            return None
        return PatientResponse.model_validate(patient)

    def create_patient(self, patient_data: PatientCreate) -> PatientResponse:
        """
        Create a new patient.

        Parameters:
            patient_data: Patient data for creation

        Returns:
            Newly created PatientResponse
        """
        patient = self.repository.create(patient_data)

        # Increment metrics
        if settings.METRICS_ENABLED:
            PATIENTS_CREATED_TOTAL.inc()

        return PatientResponse.model_validate(patient)

    def update_patient(
        self,
        patient_id: int,
        patient_data: PatientUpdate
    ) -> Optional[PatientResponse]:
        """
        Update an existing patient.

        Parameters:
            patient_id: The patient's unique identifier
            patient_data: Updated patient data

        Returns:
            Updated PatientResponse if found, None otherwise
        """
        patient = self.repository.update(patient_id, patient_data)
        if not patient:
            return None

        # Increment metrics
        if settings.METRICS_ENABLED:
            PATIENTS_UPDATED_TOTAL.inc()

        return PatientResponse.model_validate(patient)

    def delete_patient(self, patient_id: int) -> bool:
        """
        Delete a patient.

        Parameters:
            patient_id: The patient's unique identifier

        Returns:
            True if deleted, False if not found
        """
        result = self.repository.delete(patient_id)

        # Increment metrics
        if result and settings.METRICS_ENABLED:
            PATIENTS_DELETED_TOTAL.inc()

        return result
