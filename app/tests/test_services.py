"""
Service tests.

Tests for business logic services.
"""
import pytest
from datetime import date
from unittest.mock import patch, MagicMock
from app.services.patient_service import PatientService
from app.services.note_service import NoteService
from app.services.summary_service import SummaryService
from app.schemas.patient import PatientCreate, PatientUpdate
from app.schemas.note import NoteCreate
from app.schemas.summary import SummaryOptions
from datetime import datetime, timezone


class TestPatientService:
    """Tests for PatientService."""

    def test_get_patients_pagination(self, db_session, multiple_patients):
        """Test getting paginated patients."""
        service = PatientService(db_session)

        result = service.get_patients(page=1, size=5)

        assert len(result.items) == 5
        assert result.total == 15
        assert result.pages == 3

    def test_get_patients_empty(self, db_session):
        """Test getting patients when empty."""
        service = PatientService(db_session)

        result = service.get_patients()

        assert len(result.items) == 0
        assert result.total == 0

    def test_get_patient(self, db_session, sample_patient):
        """Test getting single patient."""
        service = PatientService(db_session)

        result = service.get_patient(sample_patient.id)

        assert result is not None
        assert result.name == sample_patient.name

    def test_get_patient_not_found(self, db_session):
        """Test getting non-existent patient."""
        service = PatientService(db_session)

        result = service.get_patient(9999)

        assert result is None

    def test_create_patient(self, db_session):
        """Test creating patient."""
        service = PatientService(db_session)
        data = PatientCreate(name="New Patient", date_of_birth=date(1995, 6, 15))

        result = service.create_patient(data)

        assert result.id is not None
        assert result.name == "New Patient"

    def test_update_patient(self, db_session, sample_patient):
        """Test updating patient."""
        service = PatientService(db_session)
        data = PatientUpdate(name="Updated")

        result = service.update_patient(sample_patient.id, data)

        assert result.name == "Updated"

    def test_delete_patient(self, db_session, sample_patient):
        """Test deleting patient."""
        service = PatientService(db_session)

        result = service.delete_patient(sample_patient.id)

        assert result is True


class TestNoteService:
    """Tests for NoteService."""

    def test_get_patient_notes(self, db_session, sample_patient_with_notes):
        """Test getting patient notes."""
        service = NoteService(db_session)

        result = service.get_patient_notes(sample_patient_with_notes.id)

        assert result is not None
        assert result.total == 2

    def test_get_patient_notes_not_found(self, db_session):
        """Test getting notes for non-existent patient."""
        service = NoteService(db_session)

        result = service.get_patient_notes(9999)

        assert result is None

    def test_create_note(self, db_session, sample_patient):
        """Test creating note."""
        service = NoteService(db_session)
        data = NoteCreate(
            content="New note",
            note_timestamp=datetime.now(timezone.utc)
        )

        result = service.create_note(sample_patient.id, data)

        assert result is not None
        assert result.content == "New note"

    def test_create_note_patient_not_found(self, db_session):
        """Test creating note for non-existent patient."""
        service = NoteService(db_session)
        data = NoteCreate(
            content="Test",
            note_timestamp=datetime.now(timezone.utc)
        )

        result = service.create_note(9999, data)

        assert result is None

    def test_delete_note(self, db_session, sample_patient_with_notes):
        """Test deleting note."""
        service = NoteService(db_session)
        notes = service.get_patient_notes(sample_patient_with_notes.id)
        note_id = notes.items[0].id

        result = service.delete_note(note_id)

        assert result is True

    def test_delete_patient_notes(self, db_session, sample_patient_with_notes):
        """Test deleting all patient notes."""
        service = NoteService(db_session)

        result = service.delete_patient_notes(sample_patient_with_notes.id)

        assert result == 2


class TestSummaryService:
    """Tests for SummaryService."""

    @patch('app.services.summary_service.generate_summary')
    def test_generate_patient_summary(self, mock_generate, db_session, sample_patient_with_notes):
        """Test generating patient summary."""
        mock_generate.return_value = "Test summary"
        service = SummaryService(db_session)

        result = service.generate_patient_summary(sample_patient_with_notes.id)

        assert result is not None
        assert result.heading.name == "Jane Smith"
        assert result.note_count == 2
        assert result.summary == "Test summary"

    def test_generate_summary_patient_not_found(self, db_session):
        """Test generating summary for non-existent patient."""
        service = SummaryService(db_session)

        result = service.generate_patient_summary(9999)

        assert result is None

    @patch('app.services.summary_service.generate_summary')
    def test_generate_summary_no_notes(self, mock_generate, db_session, sample_patient):
        """Test generating summary with no notes."""
        service = SummaryService(db_session)

        result = service.generate_patient_summary(sample_patient.id)

        assert result is not None
        assert result.note_count == 0
        assert "No clinical notes" in result.summary
        mock_generate.assert_not_called()

    def test_calculate_age(self, db_session):
        """Test age calculation."""
        service = SummaryService(db_session)

        # Test with a known date
        age = service._calculate_age(date(1990, 1, 1))

        assert age >= 34  # Will be 34 or 35 depending on current date

    @patch('app.services.summary_service.generate_summary')
    def test_generate_summary_with_options(self, mock_generate, db_session, sample_patient_with_notes):
        """Test generating summary with custom options."""
        mock_generate.return_value = "Custom summary"
        service = SummaryService(db_session)
        options = SummaryOptions(audience="family", max_length=300)

        result = service.generate_patient_summary(sample_patient_with_notes.id, options)

        mock_generate.assert_called_once()
        call_args = mock_generate.call_args
        assert call_args[1]['audience'] == "family"
        assert call_args[1]['max_length'] == 300
