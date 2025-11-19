"""
Note repository module.

Provides data access layer for patient medical notes.
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.note import Note
from app.schemas.note import NoteCreate


class NoteRepository:
    """
    Repository class for note database operations.

    Encapsulates all database queries related to patient notes,
    following the repository pattern for clean separation of concerns.
    """

    def __init__(self, db: Session):
        """
        Initialize repository with database session.

        Parameters:
            db: SQLAlchemy database session
        """
        self.db = db

    def get_by_patient_id(self, patient_id: int) -> list[Note]:
        """
        Retrieve all notes for a specific patient.

        Parameters:
            patient_id: The patient's unique identifier

        Returns:
            List of Note objects ordered by timestamp
        """
        return (
            self.db.query(Note)
            .filter(Note.patient_id == patient_id)
            .order_by(Note.note_timestamp)
            .all()
        )

    def get_by_id(self, note_id: int) -> Optional[Note]:
        """
        Retrieve a note by ID.

        Parameters:
            note_id: The note's unique identifier

        Returns:
            Note object if found, None otherwise
        """
        return self.db.query(Note).filter(Note.id == note_id).first()

    def create(self, patient_id: int, note_data: NoteCreate) -> Note:
        """
        Create a new note for a patient.

        Parameters:
            patient_id: The patient's unique identifier
            note_data: Note data for creation

        Returns:
            Newly created Note object
        """
        note = Note(patient_id=patient_id, **note_data.model_dump())
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return note

    def delete(self, note_id: int) -> bool:
        """
        Delete a note by ID.

        Parameters:
            note_id: The note's unique identifier

        Returns:
            True if deleted, False if not found
        """
        note = self.get_by_id(note_id)
        if not note:
            return False

        self.db.delete(note)
        self.db.commit()
        return True

    def delete_by_patient_id(self, patient_id: int) -> int:
        """
        Delete all notes for a specific patient.

        Parameters:
            patient_id: The patient's unique identifier

        Returns:
            Number of notes deleted
        """
        deleted = (
            self.db.query(Note)
            .filter(Note.patient_id == patient_id)
            .delete()
        )
        self.db.commit()
        return deleted
