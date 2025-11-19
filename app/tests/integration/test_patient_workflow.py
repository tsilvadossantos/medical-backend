"""
Integration tests for patient workflow.

Tests complete patient lifecycle including CRUD operations,
pagination, sorting, and search functionality.
"""
import pytest


class TestPatientCRUDWorkflow:
    """Test complete patient CRUD lifecycle."""

    def test_create_read_update_delete_patient(self, client):
        """Test full patient lifecycle."""
        # Create
        create_response = client.post("/api/v1/patients", json={
            "name": "Integration Test Patient",
            "date_of_birth": "1988-06-15"
        })
        assert create_response.status_code == 201
        patient = create_response.json()
        patient_id = patient["id"]
        assert patient["name"] == "Integration Test Patient"
        assert patient["date_of_birth"] == "1988-06-15"
        assert "created_at" in patient

        # Read
        get_response = client.get(f"/api/v1/patients/{patient_id}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "Integration Test Patient"

        # Update
        update_response = client.put(f"/api/v1/patients/{patient_id}", json={
            "name": "Updated Patient Name"
        })
        assert update_response.status_code == 200
        updated = update_response.json()
        assert updated["name"] == "Updated Patient Name"
        assert updated["date_of_birth"] == "1988-06-15"  # Unchanged
        assert updated["updated_at"] is not None

        # Verify update persisted
        verify_response = client.get(f"/api/v1/patients/{patient_id}")
        assert verify_response.json()["name"] == "Updated Patient Name"

        # Delete
        delete_response = client.delete(f"/api/v1/patients/{patient_id}")
        assert delete_response.status_code == 204

        # Verify deletion
        get_deleted = client.get(f"/api/v1/patients/{patient_id}")
        assert get_deleted.status_code == 404

    def test_create_multiple_patients_and_list(self, client):
        """Test creating multiple patients and listing them."""
        # Create patients
        names = ["Alice Brown", "Bob Wilson", "Carol Davis"]
        created_ids = []

        for i, name in enumerate(names):
            response = client.post("/api/v1/patients", json={
                "name": name,
                "date_of_birth": f"199{i}-01-01"
            })
            assert response.status_code == 201
            created_ids.append(response.json()["id"])

        # List all
        list_response = client.get("/api/v1/patients")
        assert list_response.status_code == 200
        data = list_response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

    def test_partial_update_preserves_fields(self, client):
        """Test that partial updates don't affect unspecified fields."""
        # Create patient
        response = client.post("/api/v1/patients", json={
            "name": "Original Name",
            "date_of_birth": "1975-12-25"
        })
        patient_id = response.json()["id"]

        # Update only name
        client.put(f"/api/v1/patients/{patient_id}", json={
            "name": "New Name"
        })

        # Verify date_of_birth unchanged
        patient = client.get(f"/api/v1/patients/{patient_id}").json()
        assert patient["name"] == "New Name"
        assert patient["date_of_birth"] == "1975-12-25"

        # Update only date_of_birth
        client.put(f"/api/v1/patients/{patient_id}", json={
            "date_of_birth": "1980-01-01"
        })

        # Verify name unchanged
        patient = client.get(f"/api/v1/patients/{patient_id}").json()
        assert patient["name"] == "New Name"
        assert patient["date_of_birth"] == "1980-01-01"


class TestPatientPagination:
    """Test patient list pagination functionality."""

    def test_pagination_first_page(self, client):
        """Test getting first page of results."""
        # Create 25 patients
        for i in range(25):
            client.post("/api/v1/patients", json={
                "name": f"Patient {i+1:02d}",
                "date_of_birth": "1990-01-01"
            })

        response = client.get("/api/v1/patients?page=1&size=10")
        data = response.json()

        assert data["total"] == 25
        assert data["page"] == 1
        assert data["size"] == 10
        assert data["pages"] == 3
        assert len(data["items"]) == 10

    def test_pagination_middle_page(self, client):
        """Test getting middle page of results."""
        for i in range(25):
            client.post("/api/v1/patients", json={
                "name": f"Patient {i+1:02d}",
                "date_of_birth": "1990-01-01"
            })

        response = client.get("/api/v1/patients?page=2&size=10")
        data = response.json()

        assert data["page"] == 2
        assert len(data["items"]) == 10

    def test_pagination_last_page(self, client):
        """Test getting last page with partial results."""
        for i in range(25):
            client.post("/api/v1/patients", json={
                "name": f"Patient {i+1:02d}",
                "date_of_birth": "1990-01-01"
            })

        response = client.get("/api/v1/patients?page=3&size=10")
        data = response.json()

        assert data["page"] == 3
        assert len(data["items"]) == 5  # Remaining items

    def test_pagination_beyond_last_page(self, client):
        """Test requesting page beyond available data."""
        for i in range(5):
            client.post("/api/v1/patients", json={
                "name": f"Patient {i+1}",
                "date_of_birth": "1990-01-01"
            })

        response = client.get("/api/v1/patients?page=10&size=10")
        data = response.json()

        assert data["total"] == 5
        assert len(data["items"]) == 0

    def test_custom_page_size(self, client):
        """Test custom page sizes."""
        for i in range(20):
            client.post("/api/v1/patients", json={
                "name": f"Patient {i+1}",
                "date_of_birth": "1990-01-01"
            })

        # Test size of 5
        response = client.get("/api/v1/patients?size=5")
        assert response.json()["pages"] == 4
        assert len(response.json()["items"]) == 5

        # Test size of 20
        response = client.get("/api/v1/patients?size=20")
        assert response.json()["pages"] == 1
        assert len(response.json()["items"]) == 20


class TestPatientSorting:
    """Test patient list sorting functionality."""

    def test_sort_by_name_ascending(self, client):
        """Test sorting patients by name ascending."""
        names = ["Zara", "Alice", "Mike"]
        for name in names:
            client.post("/api/v1/patients", json={
                "name": name,
                "date_of_birth": "1990-01-01"
            })

        response = client.get("/api/v1/patients?sort_by=name&sort_order=asc")
        items = response.json()["items"]

        assert items[0]["name"] == "Alice"
        assert items[1]["name"] == "Mike"
        assert items[2]["name"] == "Zara"

    def test_sort_by_name_descending(self, client):
        """Test sorting patients by name descending."""
        names = ["Zara", "Alice", "Mike"]
        for name in names:
            client.post("/api/v1/patients", json={
                "name": name,
                "date_of_birth": "1990-01-01"
            })

        response = client.get("/api/v1/patients?sort_by=name&sort_order=desc")
        items = response.json()["items"]

        assert items[0]["name"] == "Zara"
        assert items[1]["name"] == "Mike"
        assert items[2]["name"] == "Alice"

    def test_sort_by_date_of_birth(self, client):
        """Test sorting patients by date of birth."""
        patients = [
            ("Oldest", "1960-01-01"),
            ("Middle", "1980-01-01"),
            ("Youngest", "2000-01-01")
        ]
        for name, dob in patients:
            client.post("/api/v1/patients", json={
                "name": name,
                "date_of_birth": dob
            })

        # Ascending (oldest first)
        response = client.get("/api/v1/patients?sort_by=date_of_birth&sort_order=asc")
        items = response.json()["items"]
        assert items[0]["name"] == "Oldest"
        assert items[2]["name"] == "Youngest"

        # Descending (youngest first)
        response = client.get("/api/v1/patients?sort_by=date_of_birth&sort_order=desc")
        items = response.json()["items"]
        assert items[0]["name"] == "Youngest"
        assert items[2]["name"] == "Oldest"

    def test_sort_by_id(self, client):
        """Test sorting patients by ID."""
        for name in ["First", "Second", "Third"]:
            client.post("/api/v1/patients", json={
                "name": name,
                "date_of_birth": "1990-01-01"
            })

        # Ascending (default)
        response = client.get("/api/v1/patients?sort_by=id&sort_order=asc")
        items = response.json()["items"]
        assert items[0]["name"] == "First"

        # Descending
        response = client.get("/api/v1/patients?sort_by=id&sort_order=desc")
        items = response.json()["items"]
        assert items[0]["name"] == "Third"


class TestPatientSearch:
    """Test patient search functionality."""

    def test_search_by_exact_name(self, client):
        """Test searching for exact name match."""
        names = ["John Smith", "Jane Doe", "John Adams"]
        for name in names:
            client.post("/api/v1/patients", json={
                "name": name,
                "date_of_birth": "1990-01-01"
            })

        response = client.get("/api/v1/patients?search=John Smith")
        data = response.json()

        assert data["total"] >= 1
        assert any(p["name"] == "John Smith" for p in data["items"])

    def test_search_partial_match(self, client):
        """Test searching with partial name."""
        names = ["John Smith", "Jane Doe", "John Adams"]
        for name in names:
            client.post("/api/v1/patients", json={
                "name": name,
                "date_of_birth": "1990-01-01"
            })

        response = client.get("/api/v1/patients?search=John")
        data = response.json()

        assert data["total"] == 2
        names_found = [p["name"] for p in data["items"]]
        assert "John Smith" in names_found
        assert "John Adams" in names_found

    def test_search_case_insensitive(self, client):
        """Test case-insensitive search."""
        client.post("/api/v1/patients", json={
            "name": "UPPERCASE NAME",
            "date_of_birth": "1990-01-01"
        })

        response = client.get("/api/v1/patients?search=uppercase")
        assert response.json()["total"] >= 1

    def test_search_no_results(self, client):
        """Test search with no matching results."""
        client.post("/api/v1/patients", json={
            "name": "John Doe",
            "date_of_birth": "1990-01-01"
        })

        response = client.get("/api/v1/patients?search=NonexistentName")
        assert response.json()["total"] == 0
        assert len(response.json()["items"]) == 0

    def test_search_with_pagination(self, client):
        """Test search combined with pagination."""
        # Create 15 patients named "Test Patient X"
        for i in range(15):
            client.post("/api/v1/patients", json={
                "name": f"Test Patient {i+1}",
                "date_of_birth": "1990-01-01"
            })

        # Also create some non-matching patients
        for i in range(5):
            client.post("/api/v1/patients", json={
                "name": f"Other Person {i+1}",
                "date_of_birth": "1990-01-01"
            })

        response = client.get("/api/v1/patients?search=Test&page=1&size=10")
        data = response.json()

        assert data["total"] == 15
        assert len(data["items"]) == 10
        assert data["pages"] == 2


class TestPatientErrorHandling:
    """Test error handling for patient endpoints."""

    def test_get_nonexistent_patient(self, client):
        """Test getting a patient that doesn't exist."""
        response = client.get("/api/v1/patients/99999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Patient not found"

    def test_update_nonexistent_patient(self, client):
        """Test updating a patient that doesn't exist."""
        response = client.put("/api/v1/patients/99999", json={
            "name": "New Name"
        })
        assert response.status_code == 404

    def test_delete_nonexistent_patient(self, client):
        """Test deleting a patient that doesn't exist."""
        response = client.delete("/api/v1/patients/99999")
        assert response.status_code == 404

    def test_create_patient_missing_required_fields(self, client):
        """Test creating patient without required fields."""
        response = client.post("/api/v1/patients", json={
            "name": "Only Name"
            # Missing date_of_birth
        })
        assert response.status_code == 422

    def test_create_patient_invalid_date_format(self, client):
        """Test creating patient with invalid date format."""
        response = client.post("/api/v1/patients", json={
            "name": "Test Patient",
            "date_of_birth": "not-a-date"
        })
        assert response.status_code == 422

    def test_invalid_page_number(self, client):
        """Test requesting invalid page number."""
        response = client.get("/api/v1/patients?page=0")
        assert response.status_code == 422

    def test_invalid_page_size(self, client):
        """Test requesting invalid page size."""
        response = client.get("/api/v1/patients?size=0")
        assert response.status_code == 422

        response = client.get("/api/v1/patients?size=101")
        assert response.status_code == 422
