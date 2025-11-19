"""
Model tests.

Tests for SQLAlchemy ORM models.
"""
import pytest
from datetime import date, datetime, timezone
from app.models.patient import Patient
from app.models.note import Note


class TestPatientModel:
    """Tests for Patient model."""

    def test_create_patient(self, db_session):
        """Test creating a patient."""
        patient = Patient(
            name="Test Patient",
            date_of_birth=date(1995, 6, 15)
        )
        db_session.add(patient)
        db_session.commit()

        assert patient.id is not None
        assert patient.name == "Test Patient"
        assert patient.date_of_birth == date(1995, 6, 15)
        assert patient.created_at is not None

    def test_patient_notes_relationship(self, db_session):
        """Test patient-notes relationship."""
        patient = Patient(name="Test", date_of_birth=date(1990, 1, 1))
        db_session.add(patient)
        db_session.commit()

        note = Note(
            patient_id=patient.id,
            content="Test note",
            note_timestamp=datetime.now(timezone.utc)
        )
        db_session.add(note)
        db_session.commit()

        assert len(patient.notes) == 1
        assert patient.notes[0].content == "Test note"

    def test_patient_cascade_delete(self, db_session):
        """Test that deleting patient deletes notes."""
        patient = Patient(name="Test", date_of_birth=date(1990, 1, 1))
        db_session.add(patient)
        db_session.commit()

        note = Note(
            patient_id=patient.id,
            content="Test note",
            note_timestamp=datetime.now(timezone.utc)
        )
        db_session.add(note)
        db_session.commit()
        note_id = note.id

        db_session.delete(patient)
        db_session.commit()

        assert db_session.query(Note).filter(Note.id == note_id).first() is None


class TestNoteModel:
    """Tests for Note model."""

    def test_create_note(self, db_session, sample_patient):
        """Test creating a note."""
        note = Note(
            patient_id=sample_patient.id,
            content="Test content",
            note_timestamp=datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
        )
        db_session.add(note)
        db_session.commit()

        assert note.id is not None
        assert note.patient_id == sample_patient.id
        assert note.content == "Test content"
        assert note.created_at is not None

    def test_note_patient_relationship(self, db_session, sample_patient):
        """Test note-patient relationship."""
        note = Note(
            patient_id=sample_patient.id,
            content="Test",
            note_timestamp=datetime.now(timezone.utc)
        )
        db_session.add(note)
        db_session.commit()

        assert note.patient.name == sample_patient.name
