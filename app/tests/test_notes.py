"""
Notes endpoint tests.

Tests for patient note API operations.
"""
import pytest


class TestNoteEndpoints:
    """Tests for note CRUD endpoints."""

    def _create_patient(self, client):
        """Helper to create a patient."""
        response = client.post(
            "/patients",
            json={"name": "Test Patient", "date_of_birth": "1990-01-15"}
        )
        return response.json()["id"]

    def test_create_note(self, client):
        """Test creating a note."""
        patient_id = self._create_patient(client)

        response = client.post(
            f"/patients/{patient_id}/notes",
            json={
                "content": "Test note content",
                "note_timestamp": "2024-01-15T10:30:00Z"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Test note content"
        assert data["patient_id"] == patient_id

    def test_create_note_patient_not_found(self, client):
        """Test creating note for non-existent patient."""
        response = client.post(
            "/patients/9999/notes",
            json={
                "content": "Test",
                "note_timestamp": "2024-01-15T10:00:00Z"
            }
        )

        assert response.status_code == 404

    def test_create_note_invalid(self, client):
        """Test creating note with invalid data."""
        patient_id = self._create_patient(client)

        response = client.post(
            f"/patients/{patient_id}/notes",
            json={"note_timestamp": "2024-01-15T10:00:00Z"}  # Missing content
        )

        assert response.status_code == 422

    def test_list_patient_notes(self, client):
        """Test listing patient notes."""
        patient_id = self._create_patient(client)

        # Create multiple notes
        for i in range(3):
            client.post(
                f"/patients/{patient_id}/notes",
                json={
                    "content": f"Note {i}",
                    "note_timestamp": f"2024-01-{15+i}T10:00:00Z"
                }
            )

        response = client.get(f"/patients/{patient_id}/notes")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

    def test_list_notes_patient_not_found(self, client):
        """Test listing notes for non-existent patient."""
        response = client.get("/patients/9999/notes")

        assert response.status_code == 404

    def test_list_notes_empty(self, client):
        """Test listing notes when patient has none."""
        patient_id = self._create_patient(client)

        response = client.get(f"/patients/{patient_id}/notes")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    def test_delete_note(self, client):
        """Test deleting a specific note."""
        patient_id = self._create_patient(client)

        create_response = client.post(
            f"/patients/{patient_id}/notes",
            json={
                "content": "To delete",
                "note_timestamp": "2024-01-15T10:00:00Z"
            }
        )
        note_id = create_response.json()["id"]

        response = client.delete(f"/patients/{patient_id}/notes/{note_id}")

        assert response.status_code == 204

    def test_delete_note_not_found(self, client):
        """Test deleting non-existent note."""
        patient_id = self._create_patient(client)

        response = client.delete(f"/patients/{patient_id}/notes/9999")

        assert response.status_code == 404

    def test_delete_all_patient_notes(self, client):
        """Test deleting all notes for a patient."""
        patient_id = self._create_patient(client)

        # Create notes
        for i in range(3):
            client.post(
                f"/patients/{patient_id}/notes",
                json={
                    "content": f"Note {i}",
                    "note_timestamp": f"2024-01-{15+i}T10:00:00Z"
                }
            )

        response = client.delete(f"/patients/{patient_id}/notes")

        assert response.status_code == 200
        assert response.json()["deleted"] == 3

        # Verify deleted
        list_response = client.get(f"/patients/{patient_id}/notes")
        assert list_response.json()["total"] == 0

    def test_delete_all_notes_patient_not_found(self, client):
        """Test deleting all notes for non-existent patient."""
        response = client.delete("/patients/9999/notes")

        assert response.status_code == 404

    def test_notes_ordered_by_timestamp(self, client):
        """Test notes are ordered by timestamp."""
        patient_id = self._create_patient(client)

        # Create notes in non-chronological order
        client.post(
            f"/patients/{patient_id}/notes",
            json={"content": "Third", "note_timestamp": "2024-01-17T10:00:00Z"}
        )
        client.post(
            f"/patients/{patient_id}/notes",
            json={"content": "First", "note_timestamp": "2024-01-15T10:00:00Z"}
        )
        client.post(
            f"/patients/{patient_id}/notes",
            json={"content": "Second", "note_timestamp": "2024-01-16T10:00:00Z"}
        )

        response = client.get(f"/patients/{patient_id}/notes")

        data = response.json()
        assert data["items"][0]["content"] == "First"
        assert data["items"][1]["content"] == "Second"
        assert data["items"][2]["content"] == "Third"
