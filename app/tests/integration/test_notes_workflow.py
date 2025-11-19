"""
Integration tests for notes workflow.

Tests complete notes lifecycle including CRUD operations
and patient-note relationships.
"""
import pytest
from datetime import datetime


class TestNotesCRUDWorkflow:
    """Test complete notes CRUD lifecycle."""

    def test_create_and_list_notes_for_patient(self, client):
        """Test creating notes and listing them for a patient."""
        # Create patient first
        patient_response = client.post("/api/v1/patients", json={
            "name": "Note Test Patient",
            "date_of_birth": "1985-05-10"
        })
        patient_id = patient_response.json()["id"]

        # Create first note
        note1_response = client.post(f"/api/v1/patients/{patient_id}/notes", json={
            "content": "First medical note content",
            "note_timestamp": "2024-01-15T09:00:00Z"
        })
        assert note1_response.status_code == 201
        note1 = note1_response.json()
        assert note1["patient_id"] == patient_id
        assert note1["content"] == "First medical note content"

        # Create second note
        note2_response = client.post(f"/api/v1/patients/{patient_id}/notes", json={
            "content": "Second medical note content",
            "note_timestamp": "2024-01-16T10:00:00Z"
        })
        assert note2_response.status_code == 201

        # List notes
        list_response = client.get(f"/api/v1/patients/{patient_id}/notes")
        assert list_response.status_code == 200
        data = list_response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    def test_delete_single_note(self, client):
        """Test deleting a single note."""
        # Create patient
        patient_response = client.post("/api/v1/patients", json={
            "name": "Delete Note Test",
            "date_of_birth": "1990-01-01"
        })
        patient_id = patient_response.json()["id"]

        # Create notes
        note1 = client.post(f"/api/v1/patients/{patient_id}/notes", json={
            "content": "Note to keep",
            "note_timestamp": "2024-01-15T09:00:00Z"
        }).json()

        note2 = client.post(f"/api/v1/patients/{patient_id}/notes", json={
            "content": "Note to delete",
            "note_timestamp": "2024-01-16T10:00:00Z"
        }).json()

        # Delete second note
        delete_response = client.delete(
            f"/api/v1/patients/{patient_id}/notes/{note2['id']}"
        )
        assert delete_response.status_code == 204

        # Verify only one note remains
        list_response = client.get(f"/api/v1/patients/{patient_id}/notes")
        data = list_response.json()
        assert data["total"] == 1
        assert data["items"][0]["id"] == note1["id"]

    def test_delete_all_patient_notes(self, client):
        """Test deleting all notes for a patient."""
        # Create patient
        patient_response = client.post("/api/v1/patients", json={
            "name": "Delete All Notes Test",
            "date_of_birth": "1990-01-01"
        })
        patient_id = patient_response.json()["id"]

        # Create multiple notes
        for i in range(5):
            client.post(f"/api/v1/patients/{patient_id}/notes", json={
                "content": f"Note {i+1}",
                "note_timestamp": f"2024-01-{15+i}T09:00:00Z"
            })

        # Verify notes exist
        list_response = client.get(f"/api/v1/patients/{patient_id}/notes")
        assert list_response.json()["total"] == 5

        # Delete all notes
        delete_response = client.delete(f"/api/v1/patients/{patient_id}/notes")
        assert delete_response.status_code == 200
        assert delete_response.json()["deleted"] == 5

        # Verify no notes remain
        list_response = client.get(f"/api/v1/patients/{patient_id}/notes")
        assert list_response.json()["total"] == 0

    def test_notes_isolated_between_patients(self, client):
        """Test that notes are properly isolated between patients."""
        # Create two patients
        patient1 = client.post("/api/v1/patients", json={
            "name": "Patient One",
            "date_of_birth": "1980-01-01"
        }).json()

        patient2 = client.post("/api/v1/patients", json={
            "name": "Patient Two",
            "date_of_birth": "1985-01-01"
        }).json()

        # Create notes for patient 1
        for i in range(3):
            client.post(f"/api/v1/patients/{patient1['id']}/notes", json={
                "content": f"Patient 1 Note {i+1}",
                "note_timestamp": "2024-01-15T09:00:00Z"
            })

        # Create notes for patient 2
        for i in range(2):
            client.post(f"/api/v1/patients/{patient2['id']}/notes", json={
                "content": f"Patient 2 Note {i+1}",
                "note_timestamp": "2024-01-15T09:00:00Z"
            })

        # Verify patient 1 has 3 notes
        p1_notes = client.get(f"/api/v1/patients/{patient1['id']}/notes").json()
        assert p1_notes["total"] == 3

        # Verify patient 2 has 2 notes
        p2_notes = client.get(f"/api/v1/patients/{patient2['id']}/notes").json()
        assert p2_notes["total"] == 2

        # Verify content is correct
        for note in p1_notes["items"]:
            assert "Patient 1" in note["content"]

        for note in p2_notes["items"]:
            assert "Patient 2" in note["content"]


class TestSOAPNoteContent:
    """Test SOAP note specific functionality."""

    def test_create_full_soap_note(self, client):
        """Test creating a complete SOAP format note."""
        patient = client.post("/api/v1/patients", json={
            "name": "SOAP Test Patient",
            "date_of_birth": "1975-08-20"
        }).json()

        soap_content = """SOAP Note - Encounter Date: 2024-01-20
Patient: patient--001

S: 49 y/o male presents with 2-week history of progressive lower back pain. Pain is dull, constant, rated 6/10. Worse with prolonged sitting. No radiation to legs. No bowel/bladder changes.

O:
Vitals:
BP: 128/82 mmHg
HR: 76 bpm
Temp: 98.4°F

Spine: Mild paraspinal muscle tenderness L3-L5. No step-off. SLR negative bilat.
Neuro: Strength 5/5 LE bilat. DTRs 2+ and symmetric.

A:
Mechanical low back pain - likely muscular strain

P:
Ibuprofen 600mg TID with food x 7 days
Ice/heat alternating
Stretching exercises handout provided
Physical therapy referral if not improved in 2 weeks
Return if symptoms worsen or neurological changes

Signed:
Dr. Jennifer Lee, MD
Family Medicine"""

        note_response = client.post(f"/api/v1/patients/{patient['id']}/notes", json={
            "content": soap_content,
            "note_timestamp": "2024-01-20T14:30:00Z"
        })

        assert note_response.status_code == 201
        note = note_response.json()
        assert "SOAP Note" in note["content"]
        assert "Subjective" in note["content"] or "S:" in note["content"]

    def test_create_multiple_soap_notes_timeline(self, client):
        """Test creating multiple SOAP notes to form a timeline."""
        patient = client.post("/api/v1/patients", json={
            "name": "Timeline Test Patient",
            "date_of_birth": "1982-03-15"
        }).json()

        # Initial visit
        client.post(f"/api/v1/patients/{patient['id']}/notes", json={
            "content": "S: Initial presentation with symptoms...\nA: Initial diagnosis\nP: Begin treatment",
            "note_timestamp": "2024-01-10T09:00:00Z"
        })

        # Follow-up visit
        client.post(f"/api/v1/patients/{patient['id']}/notes", json={
            "content": "S: Partial improvement noted...\nA: Responding to treatment\nP: Continue current regimen",
            "note_timestamp": "2024-01-17T09:00:00Z"
        })

        # Final visit
        client.post(f"/api/v1/patients/{patient['id']}/notes", json={
            "content": "S: Symptoms resolved...\nA: Complete resolution\nP: Discharge from care",
            "note_timestamp": "2024-01-24T09:00:00Z"
        })

        notes = client.get(f"/api/v1/patients/{patient['id']}/notes").json()
        assert notes["total"] == 3


class TestNotesErrorHandling:
    """Test error handling for notes endpoints."""

    def test_create_note_for_nonexistent_patient(self, client):
        """Test creating note for patient that doesn't exist."""
        response = client.post("/api/v1/patients/99999/notes", json={
            "content": "Test note",
            "note_timestamp": "2024-01-15T09:00:00Z"
        })
        assert response.status_code == 404
        assert response.json()["detail"] == "Patient not found"

    def test_list_notes_for_nonexistent_patient(self, client):
        """Test listing notes for patient that doesn't exist."""
        response = client.get("/api/v1/patients/99999/notes")
        assert response.status_code == 404

    def test_delete_nonexistent_note(self, client):
        """Test deleting note that doesn't exist."""
        # Create patient
        patient = client.post("/api/v1/patients", json={
            "name": "Test Patient",
            "date_of_birth": "1990-01-01"
        }).json()

        response = client.delete(f"/api/v1/patients/{patient['id']}/notes/99999")
        assert response.status_code == 404

    def test_delete_all_notes_for_nonexistent_patient(self, client):
        """Test deleting all notes for patient that doesn't exist."""
        response = client.delete("/api/v1/patients/99999/notes")
        assert response.status_code == 404

    def test_create_note_missing_content(self, client):
        """Test creating note without content."""
        patient = client.post("/api/v1/patients", json={
            "name": "Test Patient",
            "date_of_birth": "1990-01-01"
        }).json()

        response = client.post(f"/api/v1/patients/{patient['id']}/notes", json={
            "note_timestamp": "2024-01-15T09:00:00Z"
            # Missing content
        })
        assert response.status_code == 422

    def test_create_note_missing_timestamp(self, client):
        """Test creating note without timestamp."""
        patient = client.post("/api/v1/patients", json={
            "name": "Test Patient",
            "date_of_birth": "1990-01-01"
        }).json()

        response = client.post(f"/api/v1/patients/{patient['id']}/notes", json={
            "content": "Test content"
            # Missing note_timestamp
        })
        assert response.status_code == 422

    def test_create_note_invalid_timestamp(self, client):
        """Test creating note with invalid timestamp format."""
        patient = client.post("/api/v1/patients", json={
            "name": "Test Patient",
            "date_of_birth": "1990-01-01"
        }).json()

        response = client.post(f"/api/v1/patients/{patient['id']}/notes", json={
            "content": "Test content",
            "note_timestamp": "not-a-timestamp"
        })
        assert response.status_code == 422


class TestPatientNoteCascade:
    """Test patient-note relationship behaviors."""

    def test_notes_accessible_after_patient_update(self, client):
        """Test that notes remain accessible after patient is updated."""
        # Create patient
        patient = client.post("/api/v1/patients", json={
            "name": "Original Name",
            "date_of_birth": "1990-01-01"
        }).json()

        # Create note
        note = client.post(f"/api/v1/patients/{patient['id']}/notes", json={
            "content": "Test note",
            "note_timestamp": "2024-01-15T09:00:00Z"
        }).json()

        # Update patient
        client.put(f"/api/v1/patients/{patient['id']}", json={
            "name": "Updated Name"
        })

        # Verify note still accessible
        notes = client.get(f"/api/v1/patients/{patient['id']}/notes").json()
        assert notes["total"] == 1
        assert notes["items"][0]["id"] == note["id"]

    def test_empty_notes_list(self, client):
        """Test getting notes for patient with no notes."""
        patient = client.post("/api/v1/patients", json={
            "name": "No Notes Patient",
            "date_of_birth": "1990-01-01"
        }).json()

        notes = client.get(f"/api/v1/patients/{patient['id']}/notes").json()
        assert notes["total"] == 0
        assert len(notes["items"]) == 0

    def test_delete_all_notes_returns_zero_for_empty(self, client):
        """Test deleting all notes when patient has none."""
        patient = client.post("/api/v1/patients", json={
            "name": "Empty Notes Patient",
            "date_of_birth": "1990-01-01"
        }).json()

        response = client.delete(f"/api/v1/patients/{patient['id']}/notes")
        assert response.status_code == 200
        assert response.json()["deleted"] == 0
