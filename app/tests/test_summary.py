"""
Summary endpoint tests.

Tests for patient summary generation API.
"""
import pytest
from unittest.mock import patch, MagicMock


class TestSummaryEndpoints:
    """Tests for summary generation endpoints."""

    def _create_patient_with_notes(self, client):
        """Helper to create patient with notes."""
        response = client.post(
            "/patients",
            json={"name": "Test Patient", "date_of_birth": "1990-01-15"}
        )
        patient_id = response.json()["id"]

        soap_note = """Subjective:
Patient reports persistent cough for 3 days.

Objective:
Vitals stable. Lungs clear.

Assessment:
Upper respiratory infection.

Plan:
Rest, fluids, follow up in 1 week."""

        client.post(
            f"/patients/{patient_id}/notes",
            json={"content": soap_note, "note_timestamp": "2024-01-15T10:00:00Z"}
        )

        return patient_id

    @patch('app.api.v1.summary.generate_summary_task')
    def test_create_async_summary_job(self, mock_task, client):
        """Test creating async summary job."""
        patient_id = self._create_patient_with_notes(client)

        mock_task.delay.return_value = MagicMock(id="test-job-id")

        response = client.post(f"/patients/{patient_id}/summary/async")

        assert response.status_code == 202
        data = response.json()
        assert data["job_id"] == "test-job-id"
        assert data["status"] == "queued"

    def test_create_async_summary_patient_not_found(self, client):
        """Test async summary for non-existent patient."""
        response = client.post("/patients/9999/summary/async")

        assert response.status_code == 404

    @patch('app.api.v1.summary.AsyncResult')
    def test_get_job_status_pending(self, mock_async_result, client):
        """Test getting pending job status."""
        patient_id = self._create_patient_with_notes(client)

        mock_result = MagicMock()
        mock_result.status = "PENDING"
        mock_result.ready.return_value = False
        mock_async_result.return_value = mock_result

        response = client.get(f"/patients/{patient_id}/summary/jobs/test-job-id")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending"
        assert data["result"] is None

    @patch('app.api.v1.summary.AsyncResult')
    def test_get_job_status_completed(self, mock_async_result, client):
        """Test getting completed job status."""
        patient_id = self._create_patient_with_notes(client)

        mock_result = MagicMock()
        mock_result.status = "SUCCESS"
        mock_result.ready.return_value = True
        mock_result.result = {"status": "completed", "summary": "Test"}
        mock_async_result.return_value = mock_result

        response = client.get(f"/patients/{patient_id}/summary/jobs/test-job-id")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["result"]["summary"] == "Test"

    @patch('app.api.v1.summary.AsyncResult')
    def test_get_job_status_failed(self, mock_async_result, client):
        """Test getting failed job status."""
        patient_id = self._create_patient_with_notes(client)

        mock_result = MagicMock()
        mock_result.status = "FAILURE"
        mock_result.ready.return_value = True
        mock_result.result = {"status": "error", "error": "Test error"}
        mock_async_result.return_value = mock_result

        response = client.get(f"/patients/{patient_id}/summary/jobs/test-job-id")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"

    @patch('app.services.summary_service.generate_summary')
    def test_get_sync_summary(self, mock_generate, client):
        """Test synchronous summary generation."""
        patient_id = self._create_patient_with_notes(client)
        mock_generate.return_value = "Generated summary text"

        response = client.get(f"/patients/{patient_id}/summary")

        assert response.status_code == 200
        data = response.json()
        assert "heading" in data
        assert data["heading"]["name"] == "Test Patient"
        assert data["summary"] == "Generated summary text"
        assert data["note_count"] == 1

    def test_get_sync_summary_patient_not_found(self, client):
        """Test sync summary for non-existent patient."""
        response = client.get("/patients/9999/summary")

        assert response.status_code == 404

    @patch('app.services.summary_service.generate_summary')
    def test_get_sync_summary_with_options(self, mock_generate, client):
        """Test sync summary with custom options."""
        patient_id = self._create_patient_with_notes(client)
        mock_generate.return_value = "Custom summary"

        response = client.get(
            f"/patients/{patient_id}/summary",
            params={"audience": "family", "max_length": 300}
        )

        assert response.status_code == 200
        mock_generate.assert_called_once()
        call_kwargs = mock_generate.call_args[1]
        assert call_kwargs["audience"] == "family"
        assert call_kwargs["max_length"] == 300

    @patch('app.services.summary_service.generate_summary')
    def test_get_sync_summary_no_notes(self, mock_generate, client):
        """Test sync summary when patient has no notes."""
        response = client.post(
            "/patients",
            json={"name": "No Notes", "date_of_birth": "1985-06-20"}
        )
        patient_id = response.json()["id"]

        response = client.get(f"/patients/{patient_id}/summary")

        assert response.status_code == 200
        data = response.json()
        assert data["note_count"] == 0
        assert "No clinical notes" in data["summary"]
        mock_generate.assert_not_called()
