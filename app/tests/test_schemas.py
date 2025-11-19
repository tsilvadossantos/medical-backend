"""
Schema tests.

Tests for Pydantic validation schemas.
"""
import pytest
from datetime import date, datetime, timezone
from pydantic import ValidationError
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse
from app.schemas.note import NoteCreate, NoteResponse
from app.schemas.summary import SummaryOptions, PatientHeading, SummaryResponse
from app.schemas.job import JobResponse, JobStatusResponse


class TestPatientSchemas:
    """Tests for patient schemas."""

    def test_patient_create_valid(self):
        """Test valid patient creation schema."""
        data = PatientCreate(
            name="John Doe",
            date_of_birth=date(1990, 5, 15)
        )
        assert data.name == "John Doe"
        assert data.date_of_birth == date(1990, 5, 15)

    def test_patient_create_invalid_missing_name(self):
        """Test patient creation with missing name."""
        with pytest.raises(ValidationError):
            PatientCreate(date_of_birth=date(1990, 5, 15))

    def test_patient_update_partial(self):
        """Test partial patient update."""
        data = PatientUpdate(name="New Name")
        assert data.name == "New Name"
        assert data.date_of_birth is None

    def test_patient_update_empty(self):
        """Test empty patient update is valid."""
        data = PatientUpdate()
        assert data.name is None
        assert data.date_of_birth is None

    def test_patient_response_from_attributes(self):
        """Test patient response from ORM model."""
        class MockPatient:
            id = 1
            name = "Test"
            date_of_birth = date(1990, 1, 1)
            created_at = datetime.now(timezone.utc)
            updated_at = None

        response = PatientResponse.model_validate(MockPatient())
        assert response.id == 1
        assert response.name == "Test"


class TestNoteSchemas:
    """Tests for note schemas."""

    def test_note_create_valid(self):
        """Test valid note creation schema."""
        data = NoteCreate(
            content="Test content",
            note_timestamp=datetime(2024, 1, 15, 10, 0, tzinfo=timezone.utc)
        )
        assert data.content == "Test content"

    def test_note_create_invalid_missing_content(self):
        """Test note creation with missing content."""
        with pytest.raises(ValidationError):
            NoteCreate(note_timestamp=datetime.now(timezone.utc))


class TestSummarySchemas:
    """Tests for summary schemas."""

    def test_summary_options_defaults(self):
        """Test summary options default values."""
        options = SummaryOptions()
        assert options.audience == "clinician"
        assert options.max_length == 500

    def test_summary_options_custom(self):
        """Test custom summary options."""
        options = SummaryOptions(audience="family", max_length=300)
        assert options.audience == "family"
        assert options.max_length == 300

    def test_patient_heading(self):
        """Test patient heading schema."""
        heading = PatientHeading(name="John Doe", age=35, mrn="MRN-000001")
        assert heading.name == "John Doe"
        assert heading.age == 35
        assert heading.mrn == "MRN-000001"

    def test_summary_response(self):
        """Test summary response schema."""
        heading = PatientHeading(name="Test", age=30, mrn="MRN-000001")
        response = SummaryResponse(
            heading=heading,
            summary="Test summary",
            note_count=5
        )
        assert response.note_count == 5


class TestJobSchemas:
    """Tests for job schemas."""

    def test_job_response(self):
        """Test job response schema."""
        response = JobResponse(
            job_id="abc123",
            status="queued",
            message="Job queued"
        )
        assert response.job_id == "abc123"
        assert response.status == "queued"

    def test_job_status_response(self):
        """Test job status response schema."""
        response = JobStatusResponse(
            job_id="abc123",
            status="completed",
            result={"summary": "test"}
        )
        assert response.result == {"summary": "test"}

    def test_job_status_response_no_result(self):
        """Test job status response without result."""
        response = JobStatusResponse(
            job_id="abc123",
            status="pending"
        )
        assert response.result is None
