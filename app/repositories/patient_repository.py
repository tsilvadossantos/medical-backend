"""
Patient repository module.

Provides data access layer for patient records with CRUD operations.
"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate


class PatientRepository:
    """
    Repository class for patient database operations.

    Encapsulates all database queries related to patient records,
    following the repository pattern for clean separation of concerns.
    """

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Parameters:
            db: SQLAlchemy database session
        """
        self.db = db

    def get_all(
        self,
        skip: int = 0,
        limit: int = 10,
        sort_by: str = "id",
        sort_order: str = "asc",
        search: Optional[str] = None
    ) -> tuple[list[Patient], int]:
        """
        Retrieve all patients with pagination, sorting, and optional search.

        Parameters:
            skip: Number of records to skip
            limit: Maximum number of records to return
            sort_by: Field to sort by
            sort_order: Sort direction (asc or desc)
            search: Optional fuzzy search term for name

        Returns:
            Tuple of (list of patients, total count)
        """
        query = self.db.query(Patient)

        if search:
            query = query.filter(Patient.name.ilike(f"%{search}%"))

        total = query.count()

        sort_column = getattr(Patient, sort_by, Patient.id)
        if sort_order.lower() == "desc":
            sort_column = sort_column.desc()

        patients = query.order_by(sort_column).offset(skip).limit(limit).all()
        return patients, total

    def get_by_id(self, patient_id: int) -> Optional[Patient]:
        """
        Retrieve a patient by ID.

        Parameters:
            patient_id: The patient's unique identifier

        Returns:
            Patient object if found, None otherwise
        """
        return self.db.query(Patient).filter(Patient.id == patient_id).first()

    def create(self, patient_data: PatientCreate) -> Patient:
        """
        Create a new patient record.

        Parameters:
            patient_data: Patient data for creation

        Returns:
            Newly created Patient object
        """
        patient = Patient(**patient_data.model_dump())
        self.db.add(patient)
        self.db.commit()
        self.db.refresh(patient)
        return patient

    def update(self, patient_id: int, patient_data: PatientUpdate) -> Optional[Patient]:
        """
        Update an existing patient record.

        Parameters:
            patient_id: The patient's unique identifier
            patient_data: Updated patient data

        Returns:
            Updated Patient object if found, None otherwise
        """
        patient = self.get_by_id(patient_id)
        if not patient:
            return None

        update_data = patient_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(patient, field, value)

        self.db.commit()
        self.db.refresh(patient)
        return patient

    def delete(self, patient_id: int) -> bool:
        """
        Delete a patient record.

        Parameters:
            patient_id: The patient's unique identifier

        Returns:
            True if deleted, False if not found
        """
        patient = self.get_by_id(patient_id)
        if not patient:
            return False

        self.db.delete(patient)
        self.db.commit()
        return True
