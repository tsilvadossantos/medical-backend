"""
Note service module.

Provides business logic for patient note operations.
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.note_repository import NoteRepository
from app.repositories.patient_repository import PatientRepository
from app.schemas.note import NoteCreate, NoteResponse, NoteListResponse


class NoteService:
    """
    Service class for note business logic.

    Coordinates between API layer and repository layer,
    applying business rules and transformations.
    """

    def __init__(self, db: Session):
        """
        Initialize service with database session.

        Parameters:
            db: SQLAlchemy database session
        """
        self.note_repository = NoteRepository(db)
        self.patient_repository = PatientRepository(db)

    def get_patient_notes(self, patient_id: int) -> Optional[NoteListResponse]:
        """
        Get all notes for a patient.

        Parameters:
            patient_id: The patient's unique identifier

        Returns:
            NoteListResponse if patient exists, None otherwise
        """
        patient = self.patient_repository.get_by_id(patient_id)
        if not patient:
            return None

        notes = self.note_repository.get_by_patient_id(patient_id)
        return NoteListResponse(
            items=[NoteResponse.model_validate(n) for n in notes],
            total=len(notes)
        )

    def create_note(
        self,
        patient_id: int,
        note_data: NoteCreate
    ) -> Optional[NoteResponse]:
        """
        Create a new note for a patient.

        Parameters:
            patient_id: The patient's unique identifier
            note_data: Note data for creation

        Returns:
            NoteResponse if patient exists, None otherwise
        """
        patient = self.patient_repository.get_by_id(patient_id)
        if not patient:
            return None

        note = self.note_repository.create(patient_id, note_data)
        return NoteResponse.model_validate(note)

    def delete_note(self, note_id: int) -> bool:
        """
        Delete a note by ID.

        Parameters:
            note_id: The note's unique identifier

        Returns:
            True if deleted, False if not found
        """
        return self.note_repository.delete(note_id)

    def delete_patient_notes(self, patient_id: int) -> Optional[int]:
        """
        Delete all notes for a patient.

        Parameters:
            patient_id: The patient's unique identifier

        Returns:
            Number of notes deleted if patient exists, None otherwise
        """
        patient = self.patient_repository.get_by_id(patient_id)
        if not patient:
            return None

        return self.note_repository.delete_by_patient_id(patient_id)
