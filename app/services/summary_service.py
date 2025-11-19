"""
Summary service module.

Provides business logic for generating patient summaries.
"""
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from app.repositories.patient_repository import PatientRepository
from app.repositories.note_repository import NoteRepository
from app.schemas.summary import SummaryResponse, SummaryOptions, PatientHeading
from app.utils.llm_client import generate_summary


class SummaryService:
    """
    Service class for patient summary generation.

    Synthesizes patient information and notes into coherent summaries
    using either LLM-based or rule-based approaches.
    """

    def __init__(self, db: Session):
        """
        Initialize service with database session.

        Parameters:
            db: SQLAlchemy database session
        """
        self.patient_repository = PatientRepository(db)
        self.note_repository = NoteRepository(db)

    def generate_patient_summary(
        self,
        patient_id: int,
        options: Optional[SummaryOptions] = None
    ) -> Optional[SummaryResponse]:
        """
        Generate a summary for a patient based on their profile and notes.

        Parameters:
            patient_id: The patient's unique identifier
            options: Optional customization options for summary generation

        Returns:
            SummaryResponse if patient exists, None otherwise
        """
        patient = self.patient_repository.get_by_id(patient_id)
        if not patient:
            return None

        notes = self.note_repository.get_by_patient_id(patient_id)

        age = self._calculate_age(patient.date_of_birth)
        mrn = f"MRN-{patient_id:06d}"

        heading = PatientHeading(
            name=patient.name,
            age=age,
            mrn=mrn
        )

        if not options:
            options = SummaryOptions()

        notes_text = "\n\n".join([
            f"[{note.note_timestamp.strftime('%Y-%m-%d %H:%M')}]\n{note.content}"
            for note in notes
        ])

        if notes:
            summary_text = generate_summary(
                patient_name=patient.name,
                age=age,
                notes_text=notes_text,
                audience=options.audience,
                max_length=options.max_length
            )
        else:
            summary_text = f"No clinical notes available for {patient.name}."

        return SummaryResponse(
            heading=heading,
            summary=summary_text,
            note_count=len(notes)
        )

    def _calculate_age(self, birth_date: date) -> int:
        """
        Calculate age in years from birth date.

        Parameters:
            birth_date: Patient's date of birth

        Returns:
            Age in years
        """
        today = date.today()
        age = today.year - birth_date.year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        return age
