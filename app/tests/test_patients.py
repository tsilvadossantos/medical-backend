"""
Patient endpoint tests.

Tests for patient CRUD API operations.
"""
import pytest


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self, client):
        """Test health check returns ok."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestPatientEndpoints:
    """Tests for patient CRUD endpoints."""

    def test_create_patient(self, client):
        """Test creating a patient."""
        response = client.post(
            "/patients",
            json={"name": "Test Patient", "date_of_birth": "1990-01-15"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Patient"
        assert "id" in data
        assert "created_at" in data

    def test_create_patient_invalid(self, client):
        """Test creating patient with invalid data."""
        response = client.post(
            "/patients",
            json={"date_of_birth": "1990-01-15"}  # Missing name
        )

        assert response.status_code == 422

    def test_get_patient(self, client):
        """Test getting a patient by ID."""
        # Create patient first
        create_response = client.post(
            "/patients",
            json={"name": "Test Patient", "date_of_birth": "1990-01-15"}
        )
        patient_id = create_response.json()["id"]

        response = client.get(f"/patients/{patient_id}")

        assert response.status_code == 200
        assert response.json()["name"] == "Test Patient"

    def test_get_patient_not_found(self, client):
        """Test getting non-existent patient."""
        response = client.get("/patients/9999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_list_patients(self, client):
        """Test listing patients."""
        # Create some patients
        for i in range(3):
            client.post(
                "/patients",
                json={"name": f"Patient {i}", "date_of_birth": "1990-01-01"}
            )

        response = client.get("/patients")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

    def test_list_patients_pagination(self, client):
        """Test patient list pagination."""
        # Create 15 patients
        for i in range(15):
            client.post(
                "/patients",
                json={"name": f"Patient {i:02d}", "date_of_birth": "1990-01-01"}
            )

        response = client.get("/patients?page=2&size=5")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 15
        assert len(data["items"]) == 5
        assert data["page"] == 2
        assert data["pages"] == 3

    def test_list_patients_search(self, client):
        """Test patient list search."""
        client.post(
            "/patients",
            json={"name": "John Smith", "date_of_birth": "1990-01-01"}
        )
        client.post(
            "/patients",
            json={"name": "Jane Doe", "date_of_birth": "1990-01-01"}
        )

        response = client.get("/patients?search=John")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["name"] == "John Smith"

    def test_list_patients_sorting(self, client):
        """Test patient list sorting."""
        client.post(
            "/patients",
            json={"name": "Zebra", "date_of_birth": "1990-01-01"}
        )
        client.post(
            "/patients",
            json={"name": "Alpha", "date_of_birth": "1990-01-01"}
        )

        response = client.get("/patients?sort_by=name&sort_order=asc")

        assert response.status_code == 200
        data = response.json()
        assert data["items"][0]["name"] == "Alpha"

    def test_update_patient(self, client):
        """Test updating a patient."""
        create_response = client.post(
            "/patients",
            json={"name": "Original Name", "date_of_birth": "1990-01-15"}
        )
        patient_id = create_response.json()["id"]

        response = client.put(
            f"/patients/{patient_id}",
            json={"name": "Updated Name"}
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    def test_update_patient_not_found(self, client):
        """Test updating non-existent patient."""
        response = client.put(
            "/patients/9999",
            json={"name": "Test"}
        )

        assert response.status_code == 404

    def test_delete_patient(self, client):
        """Test deleting a patient."""
        create_response = client.post(
            "/patients",
            json={"name": "To Delete", "date_of_birth": "1990-01-15"}
        )
        patient_id = create_response.json()["id"]

        response = client.delete(f"/patients/{patient_id}")

        assert response.status_code == 204

        # Verify deleted
        get_response = client.get(f"/patients/{patient_id}")
        assert get_response.status_code == 404

    def test_delete_patient_not_found(self, client):
        """Test deleting non-existent patient."""
        response = client.delete("/patients/9999")

        assert response.status_code == 404
