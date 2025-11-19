"""
Integration tests for database operations.

Tests database transactions, data integrity, and concurrent operations.
"""
import pytest
from datetime import date, datetime, timezone


class TestDatabaseTransactions:
    """Test database transaction behavior."""

    def test_patient_creation_atomicity(self, client, db_session):
        """Test that patient creation is atomic."""
        # Create patient
        response = client.post("/api/v1/patients", json={
            "name": "Atomic Test Patient",
            "date_of_birth": "1990-01-01"
        })
        assert response.status_code == 201

        # Verify in database
        from app.models.patient import Patient
        patient = db_session.query(Patient).filter_by(
            name="Atomic Test Patient"
        ).first()
        assert patient is not None

    def test_note_creation_atomicity(self, client, db_session):
        """Test that note creation is atomic."""
        # Create patient
        patient = client.post("/api/v1/patients", json={
            "name": "Note Atomic Test",
            "date_of_birth": "1990-01-01"
        }).json()

        # Create note
        response = client.post(f"/api/v1/patients/{patient['id']}/notes", json={
            "content": "Atomic note test",
            "note_timestamp": "2024-01-15T09:00:00Z"
        })
        assert response.status_code == 201

        # Verify in database
        from app.models.note import Note
        note = db_session.query(Note).filter_by(
            patient_id=patient["id"]
        ).first()
        assert note is not None
        assert note.content == "Atomic note test"

    def test_update_isolation(self, client):
        """Test that updates are properly isolated."""
        # Create two patients
        patient1 = client.post("/api/v1/patients", json={
            "name": "Patient One",
            "date_of_birth": "1980-01-01"
        }).json()

        patient2 = client.post("/api/v1/patients", json={
            "name": "Patient Two",
            "date_of_birth": "1985-01-01"
        }).json()

        # Update patient 1
        client.put(f"/api/v1/patients/{patient1['id']}", json={
            "name": "Updated Patient One"
        })

        # Verify patient 2 is unchanged
        p2 = client.get(f"/api/v1/patients/{patient2['id']}").json()
        assert p2["name"] == "Patient Two"

    def test_delete_isolation(self, client):
        """Test that deletes are properly isolated."""
        # Create two patients
        patient1 = client.post("/api/v1/patients", json={
            "name": "Delete Test One",
            "date_of_birth": "1980-01-01"
        }).json()

        patient2 = client.post("/api/v1/patients", json={
            "name": "Delete Test Two",
            "date_of_birth": "1985-01-01"
        }).json()

        # Delete patient 1
        client.delete(f"/api/v1/patients/{patient1['id']}")

        # Verify patient 2 still exists
        response = client.get(f"/api/v1/patients/{patient2['id']}")
        assert response.status_code == 200


class TestDataIntegrity:
    """Test data integrity constraints."""

    def test_patient_note_foreign_key(self, client, db_session):
        """Test that notes maintain foreign key to patient."""
        # Create patient
        patient = client.post("/api/v1/patients", json={
            "name": "FK Test Patient",
            "date_of_birth": "1990-01-01"
        }).json()

        # Create note
        note = client.post(f"/api/v1/patients/{patient['id']}/notes", json={
            "content": "FK test note",
            "note_timestamp": "2024-01-15T09:00:00Z"
        }).json()

        # Verify foreign key relationship
        from app.models.note import Note
        db_note = db_session.query(Note).filter_by(id=note["id"]).first()
        assert db_note.patient_id == patient["id"]

    def test_timestamps_auto_generated(self, client):
        """Test that timestamps are automatically generated."""
        # Create patient
        patient = client.post("/api/v1/patients", json={
            "name": "Timestamp Test",
            "date_of_birth": "1990-01-01"
        }).json()

        assert patient["created_at"] is not None
        assert patient["updated_at"] is None

        # Update patient
        updated = client.put(f"/api/v1/patients/{patient['id']}", json={
            "name": "Updated Timestamp Test"
        }).json()

        assert updated["updated_at"] is not None

    def test_patient_id_uniqueness(self, client):
        """Test that patient IDs are unique and auto-incremented."""
        ids = []
        for i in range(5):
            patient = client.post("/api/v1/patients", json={
                "name": f"Unique ID Test {i}",
                "date_of_birth": "1990-01-01"
            }).json()
            ids.append(patient["id"])

        # All IDs should be unique
        assert len(ids) == len(set(ids))

        # IDs should be sequential
        for i in range(1, len(ids)):
            assert ids[i] > ids[i-1]

    def test_note_id_uniqueness(self, client):
        """Test that note IDs are unique across patients."""
        # Create two patients
        patient1 = client.post("/api/v1/patients", json={
            "name": "Note ID Test 1",
            "date_of_birth": "1990-01-01"
        }).json()

        patient2 = client.post("/api/v1/patients", json={
            "name": "Note ID Test 2",
            "date_of_birth": "1990-01-01"
        }).json()

        # Create notes for both patients
        note_ids = []
        for patient_id in [patient1["id"], patient2["id"]]:
            for i in range(3):
                note = client.post(f"/api/v1/patients/{patient_id}/notes", json={
                    "content": f"Note {i}",
                    "note_timestamp": "2024-01-15T09:00:00Z"
                }).json()
                note_ids.append(note["id"])

        # All note IDs should be unique
        assert len(note_ids) == len(set(note_ids))


class TestConcurrentOperations:
    """Test concurrent database operations."""

    def test_multiple_patients_sequential_creation(self, client):
        """Test creating multiple patients sequentially."""
        for i in range(10):
            response = client.post("/api/v1/patients", json={
                "name": f"Sequential Patient {i+1}",
                "date_of_birth": "1990-01-01"
            })
            assert response.status_code == 201

        # Verify all created
        list_response = client.get("/api/v1/patients?size=100")
        assert list_response.json()["total"] == 10

    def test_multiple_notes_sequential_creation(self, client):
        """Test creating multiple notes sequentially."""
        patient = client.post("/api/v1/patients", json={
            "name": "Multiple Notes Patient",
            "date_of_birth": "1990-01-01"
        }).json()

        for i in range(10):
            response = client.post(f"/api/v1/patients/{patient['id']}/notes", json={
                "content": f"Sequential Note {i+1}",
                "note_timestamp": f"2024-01-{15+i % 15}T09:00:00Z"
            })
            assert response.status_code == 201

        # Verify all created
        notes = client.get(f"/api/v1/patients/{patient['id']}/notes").json()
        assert notes["total"] == 10


class TestDataPersistence:
    """Test data persistence across operations."""

    def test_patient_data_persists_after_creation(self, client):
        """Test that patient data persists correctly."""
        original_data = {
            "name": "Persistence Test",
            "date_of_birth": "1985-07-22"
        }

        created = client.post("/api/v1/patients", json=original_data).json()
        retrieved = client.get(f"/api/v1/patients/{created['id']}").json()

        assert retrieved["name"] == original_data["name"]
        assert retrieved["date_of_birth"] == original_data["date_of_birth"]

    def test_note_data_persists_after_creation(self, client):
        """Test that note data persists correctly."""
        patient = client.post("/api/v1/patients", json={
            "name": "Note Persistence Test",
            "date_of_birth": "1990-01-01"
        }).json()

        original_content = "This is the original note content with special chars: @#$%"
        created = client.post(f"/api/v1/patients/{patient['id']}/notes", json={
            "content": original_content,
            "note_timestamp": "2024-01-15T09:30:45Z"
        }).json()

        notes = client.get(f"/api/v1/patients/{patient['id']}/notes").json()
        assert notes["items"][0]["content"] == original_content

    def test_update_persists_correctly(self, client):
        """Test that updates persist correctly."""
        # Create
        patient = client.post("/api/v1/patients", json={
            "name": "Original Name",
            "date_of_birth": "1990-01-01"
        }).json()

        # Update
        client.put(f"/api/v1/patients/{patient['id']}", json={
            "name": "Updated Name",
            "date_of_birth": "1991-02-02"
        })

        # Retrieve and verify
        retrieved = client.get(f"/api/v1/patients/{patient['id']}").json()
        assert retrieved["name"] == "Updated Name"
        assert retrieved["date_of_birth"] == "1991-02-02"


class TestEdgeCases:
    """Test database edge cases."""

    def test_large_note_content(self, client):
        """Test storing large note content."""
        patient = client.post("/api/v1/patients", json={
            "name": "Large Note Test",
            "date_of_birth": "1990-01-01"
        }).json()

        # Create note with large content
        large_content = "A" * 10000  # 10KB of text
        response = client.post(f"/api/v1/patients/{patient['id']}/notes", json={
            "content": large_content,
            "note_timestamp": "2024-01-15T09:00:00Z"
        })

        assert response.status_code == 201

        # Verify content stored correctly
        notes = client.get(f"/api/v1/patients/{patient['id']}/notes").json()
        assert len(notes["items"][0]["content"]) == 10000

    def test_special_characters_in_name(self, client):
        """Test patient names with special characters."""
        special_names = [
            "O'Brien",
            "María García",
            "Jean-Pierre",
            "김철수",
            "Müller"
        ]

        for name in special_names:
            response = client.post("/api/v1/patients", json={
                "name": name,
                "date_of_birth": "1990-01-01"
            })
            assert response.status_code == 201
            assert response.json()["name"] == name

    def test_boundary_dates(self, client):
        """Test boundary date values."""
        dates = [
            "1900-01-01",  # Very old
            "2023-12-31",  # Recent
        ]

        for dob in dates:
            response = client.post("/api/v1/patients", json={
                "name": f"Date Test {dob}",
                "date_of_birth": dob
            })
            assert response.status_code == 201
            assert response.json()["date_of_birth"] == dob

    def test_note_with_multiline_content(self, client):
        """Test note with multiline SOAP format."""
        patient = client.post("/api/v1/patients", json={
            "name": "Multiline Test",
            "date_of_birth": "1990-01-01"
        }).json()

        multiline_content = """SOAP Note - Encounter Date: 2024-01-15

S: Patient reports symptoms.
Multiple lines of subjective data.

O:
Vitals:
BP: 120/80
HR: 72

A:
Assessment line 1
Assessment line 2

P:
Plan step 1
Plan step 2"""

        response = client.post(f"/api/v1/patients/{patient['id']}/notes", json={
            "content": multiline_content,
            "note_timestamp": "2024-01-15T09:00:00Z"
        })

        assert response.status_code == 201

        # Verify multiline preserved
        notes = client.get(f"/api/v1/patients/{patient['id']}/notes").json()
        assert "\n" in notes["items"][0]["content"]
        assert notes["items"][0]["content"] == multiline_content


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check_returns_ok(self, client):
        """Test that health check returns ok status."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_health_check_always_available(self, client):
        """Test that health check is always available."""
        # Multiple calls should always succeed
        for _ in range(5):
            response = client.get("/health")
            assert response.status_code == 200
