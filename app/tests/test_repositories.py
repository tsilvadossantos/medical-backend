"""
Repository tests.

Tests for data access layer repositories.
"""
import pytest
from datetime import date, datetime, timezone
from app.repositories.patient_repository import PatientRepository
from app.repositories.note_repository import NoteRepository
from app.schemas.patient import PatientCreate, PatientUpdate
from app.schemas.note import NoteCreate


class TestPatientRepository:
    """Tests for PatientRepository."""

    def test_create_patient(self, db_session):
        """Test creating a patient."""
        repo = PatientRepository(db_session)
        data = PatientCreate(name="Test", date_of_birth=date(1990, 1, 1))

        patient = repo.create(data)

        assert patient.id is not None
        assert patient.name == "Test"

    def test_get_by_id(self, db_session, sample_patient):
        """Test getting patient by ID."""
        repo = PatientRepository(db_session)

        patient = repo.get_by_id(sample_patient.id)

        assert patient is not None
        assert patient.name == sample_patient.name

    def test_get_by_id_not_found(self, db_session):
        """Test getting non-existent patient."""
        repo = PatientRepository(db_session)

        patient = repo.get_by_id(9999)

        assert patient is None

    def test_get_all_pagination(self, db_session, multiple_patients):
        """Test pagination."""
        repo = PatientRepository(db_session)

        patients, total = repo.get_all(skip=0, limit=5)

        assert len(patients) == 5
        assert total == 15

    def test_get_all_sorting(self, db_session, multiple_patients):
        """Test sorting."""
        repo = PatientRepository(db_session)

        patients, _ = repo.get_all(sort_by="name", sort_order="desc")

        assert patients[0].name > patients[-1].name

    def test_get_all_search(self, db_session, multiple_patients):
        """Test search filtering."""
        repo = PatientRepository(db_session)

        patients, total = repo.get_all(search="Patient 01")

        assert total == 1
        assert patients[0].name == "Patient 01"

    def test_update_patient(self, db_session, sample_patient):
        """Test updating patient."""
        repo = PatientRepository(db_session)
        update_data = PatientUpdate(name="Updated Name")

        updated = repo.update(sample_patient.id, update_data)

        assert updated.name == "Updated Name"
        assert updated.date_of_birth == sample_patient.date_of_birth

    def test_update_patient_not_found(self, db_session):
        """Test updating non-existent patient."""
        repo = PatientRepository(db_session)
        update_data = PatientUpdate(name="Test")

        result = repo.update(9999, update_data)

        assert result is None

    def test_delete_patient(self, db_session, sample_patient):
        """Test deleting patient."""
        repo = PatientRepository(db_session)

        result = repo.delete(sample_patient.id)

        assert result is True
        assert repo.get_by_id(sample_patient.id) is None

    def test_delete_patient_not_found(self, db_session):
        """Test deleting non-existent patient."""
        repo = PatientRepository(db_session)

        result = repo.delete(9999)

        assert result is False


class TestNoteRepository:
    """Tests for NoteRepository."""

    def test_create_note(self, db_session, sample_patient):
        """Test creating a note."""
        repo = NoteRepository(db_session)
        data = NoteCreate(
            content="Test note",
            note_timestamp=datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
        )

        note = repo.create(sample_patient.id, data)

        assert note.id is not None
        assert note.patient_id == sample_patient.id

    def test_get_by_patient_id(self, db_session, sample_patient_with_notes):
        """Test getting notes by patient ID."""
        repo = NoteRepository(db_session)

        notes = repo.get_by_patient_id(sample_patient_with_notes.id)

        assert len(notes) == 2
        # Should be ordered by timestamp
        assert notes[0].note_timestamp < notes[1].note_timestamp

    def test_get_by_patient_id_empty(self, db_session, sample_patient):
        """Test getting notes for patient with no notes."""
        repo = NoteRepository(db_session)

        notes = repo.get_by_patient_id(sample_patient.id)

        assert len(notes) == 0

    def test_get_by_id(self, db_session, sample_patient):
        """Test getting note by ID."""
        repo = NoteRepository(db_session)
        data = NoteCreate(
            content="Test",
            note_timestamp=datetime.now(timezone.utc)
        )
        note = repo.create(sample_patient.id, data)

        found = repo.get_by_id(note.id)

        assert found is not None
        assert found.content == "Test"

    def test_delete_note(self, db_session, sample_patient):
        """Test deleting a note."""
        repo = NoteRepository(db_session)
        data = NoteCreate(
            content="To delete",
            note_timestamp=datetime.now(timezone.utc)
        )
        note = repo.create(sample_patient.id, data)

        result = repo.delete(note.id)

        assert result is True
        assert repo.get_by_id(note.id) is None

    def test_delete_note_not_found(self, db_session):
        """Test deleting non-existent note."""
        repo = NoteRepository(db_session)

        result = repo.delete(9999)

        assert result is False

    def test_delete_by_patient_id(self, db_session, sample_patient_with_notes):
        """Test deleting all notes for a patient."""
        repo = NoteRepository(db_session)

        deleted = repo.delete_by_patient_id(sample_patient_with_notes.id)

        assert deleted == 2
        assert len(repo.get_by_patient_id(sample_patient_with_notes.id)) == 0
