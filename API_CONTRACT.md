# Healthcare Medical Backend - API Contract

**Version:** 1.0.0
**Base URL:** `http://localhost:8000/api/v1`
**Content-Type:** `application/json`

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Common Response Formats](#common-response-formats)
4. [Error Handling](#error-handling)
5. [Endpoints](#endpoints)
   - [Health Check](#health-check)
   - [Patients](#patients)
   - [Notes](#notes)
   - [Summary](#summary)

---

## Overview

This API provides healthcare patient management services including:
- Patient record management (CRUD operations)
- Medical notes management (SOAP format)
- AI-powered patient summary generation (sync and async)

### Technical Stack
- **Framework:** FastAPI
- **Database:** PostgreSQL
- **Job Queue:** Redis + Celery
- **AI Providers:** Ollama (default), OpenAI, Anthropic

---

## Authentication

Currently, this API does not require authentication. Future versions will implement:
- JWT Bearer tokens
- API key authentication
- Role-based access control

---

## Common Response Formats

### Success Response
```json
{
  "field": "value"
}
```

### Paginated Response
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 10,
  "pages": 10
}
```

### Job Response
```json
{
  "job_id": "uuid",
  "status": "queued|pending|processing|completed|failed",
  "message": "Description"
}
```

---

## Error Handling

### Error Response Format
```json
{
  "detail": "Error message description"
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 202 | Accepted (async job queued) |
| 204 | No Content (successful deletion) |
| 400 | Bad Request |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

---

## Endpoints

---

### Health Check

#### GET /health

Check application health status.

**Request:**
```
GET /health
```

**Response:** `200 OK`
```json
{
  "status": "ok"
}
```

---

### Patients

#### GET /api/v1/patients

List all patients with pagination, sorting, and search.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number (1-indexed) |
| `size` | integer | 10 | Items per page (1-100) |
| `sort_by` | string | "id" | Field to sort by (id, name, date_of_birth, created_at) |
| `sort_order` | string | "asc" | Sort direction (asc, desc) |
| `search` | string | null | Search term for patient name (fuzzy match) |

**Request:**
```
GET /api/v1/patients?page=1&size=10&sort_by=name&sort_order=asc&search=john
```

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": 1,
      "name": "John Smith",
      "date_of_birth": "1985-03-15",
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-16T08:00:00"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 10,
  "pages": 1
}
```

---

#### GET /api/v1/patients/{patient_id}

Get a specific patient by ID.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `patient_id` | integer | Patient's unique identifier |

**Request:**
```
GET /api/v1/patients/1
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "John Smith",
  "date_of_birth": "1985-03-15",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-16T08:00:00"
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Patient not found"
}
```

---

#### POST /api/v1/patients

Create a new patient.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Patient's full name |
| `date_of_birth` | date | Yes | Date of birth (YYYY-MM-DD) |

**Request:**
```
POST /api/v1/patients
Content-Type: application/json

{
  "name": "Jane Doe",
  "date_of_birth": "1990-07-22"
}
```

**Response:** `201 Created`
```json
{
  "id": 2,
  "name": "Jane Doe",
  "date_of_birth": "1990-07-22",
  "created_at": "2024-01-18T14:20:00",
  "updated_at": null
}
```

---

#### PUT /api/v1/patients/{patient_id}

Update an existing patient.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `patient_id` | integer | Patient's unique identifier |

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | No | Patient's full name |
| `date_of_birth` | date | No | Date of birth (YYYY-MM-DD) |

**Request:**
```
PUT /api/v1/patients/1
Content-Type: application/json

{
  "name": "John A. Smith"
}
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "name": "John A. Smith",
  "date_of_birth": "1985-03-15",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-18T14:25:00"
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Patient not found"
}
```

---

#### DELETE /api/v1/patients/{patient_id}

Delete a patient.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `patient_id` | integer | Patient's unique identifier |

**Request:**
```
DELETE /api/v1/patients/1
```

**Response:** `204 No Content`

**Error Response:** `404 Not Found`
```json
{
  "detail": "Patient not found"
}
```

---

### Notes

#### GET /api/v1/patients/{patient_id}/notes

Get all notes for a patient.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `patient_id` | integer | Patient's unique identifier |

**Request:**
```
GET /api/v1/patients/1/notes
```

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": 1,
      "patient_id": 1,
      "content": "SOAP Note - Encounter Date: 2024-01-15\nPatient: patient--001\n\nS: 45 y/o male presenting with chest pain...",
      "note_timestamp": "2024-01-15T09:00:00",
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "total": 1
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Patient not found"
}
```

---

#### POST /api/v1/patients/{patient_id}/notes

Create a new note for a patient.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `patient_id` | integer | Patient's unique identifier |

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `content` | string | Yes | Note content (SOAP format recommended) |
| `note_timestamp` | datetime | Yes | Timestamp of the medical encounter |

**Request:**
```
POST /api/v1/patients/1/notes
Content-Type: application/json

{
  "content": "SOAP Note - Encounter Date: 2024-01-20\nPatient: patient--001\n\nS: Follow-up visit...",
  "note_timestamp": "2024-01-20T10:00:00"
}
```

**Response:** `201 Created`
```json
{
  "id": 2,
  "patient_id": 1,
  "content": "SOAP Note - Encounter Date: 2024-01-20...",
  "note_timestamp": "2024-01-20T10:00:00",
  "created_at": "2024-01-20T10:30:00"
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Patient not found"
}
```

---

#### DELETE /api/v1/patients/{patient_id}/notes/{note_id}

Delete a specific note.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `patient_id` | integer | Patient's unique identifier |
| `note_id` | integer | Note's unique identifier |

**Request:**
```
DELETE /api/v1/patients/1/notes/2
```

**Response:** `204 No Content`

**Error Response:** `404 Not Found`
```json
{
  "detail": "Note not found"
}
```

---

#### DELETE /api/v1/patients/{patient_id}/notes

Delete all notes for a patient.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `patient_id` | integer | Patient's unique identifier |

**Request:**
```
DELETE /api/v1/patients/1/notes
```

**Response:** `200 OK`
```json
{
  "deleted": 5
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Patient not found"
}
```

---

### Summary

#### GET /api/v1/patients/{patient_id}/summary

Generate a patient summary synchronously.

Synthesizes patient profile and all medical notes into a coherent narrative tailored to the specified audience using AI.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `patient_id` | integer | Patient's unique identifier |

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `audience` | string | "clinician" | Target audience: "clinician" or "family" |
| `max_length` | integer | 500 | Maximum summary length in characters (100-2000) |

**Request:**
```
GET /api/v1/patients/1/summary?audience=clinician&max_length=500
```

**Response:** `200 OK`
```json
{
  "heading": {
    "name": "John Smith",
    "age": 45,
    "mrn": "MRN-00001"
  },
  "summary": "This 45-year-old male patient presented with acute chest pain on January 15, 2024. Initial evaluation revealed ST-elevation myocardial infarction (STEMI). Patient underwent emergent cardiac catheterization with successful PCI to LAD. Currently stable on dual antiplatelet therapy with aspirin and clopidogrel. Follow-up echocardiogram scheduled in 4 weeks to assess LV function. Cardiac rehabilitation referral initiated.",
  "note_count": 3
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Patient not found"
}
```

---

#### POST /api/v1/patients/{patient_id}/summary/async

Queue a summary generation job for asynchronous processing.

Returns immediately with a job ID for polling. Use this for non-blocking operations.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `patient_id` | integer | Patient's unique identifier |

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `audience` | string | "clinician" | Target audience: "clinician" or "family" |
| `max_length` | integer | 500 | Maximum summary length in characters (100-2000) |

**Request:**
```
POST /api/v1/patients/1/summary/async?audience=family&max_length=300
```

**Response:** `202 Accepted`
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "queued",
  "message": "Summary generation queued for patient 1"
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "Patient not found"
}
```

---

#### GET /api/v1/patients/{patient_id}/summary/jobs/{job_id}

Get the status of an async summary generation job.

Poll this endpoint to check job progress and retrieve results when completed.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `patient_id` | integer | Patient's unique identifier |
| `job_id` | string | Job's unique identifier (UUID) |

**Request:**
```
GET /api/v1/patients/1/summary/jobs/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Response (Processing):** `200 OK`
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "processing",
  "result": null
}
```

**Response (Completed):** `200 OK`
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "completed",
  "result": {
    "heading": {
      "name": "John Smith",
      "age": 45,
      "mrn": "MRN-00001"
    },
    "summary": "Your family member John is recovering well from a heart procedure...",
    "note_count": 3
  }
}
```

**Response (Failed):** `200 OK`
```json
{
  "job_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "failed",
  "result": {
    "error": "LLM provider unavailable"
  }
}
```

**Job Status Values:**

| Status | Description |
|--------|-------------|
| `pending` | Job queued, waiting to start |
| `processing` | Job currently running |
| `completed` | Job finished successfully |
| `failed` | Job failed with error |
| `cancelled` | Job was cancelled |

---

## Data Models

### Patient

```json
{
  "id": "integer",
  "name": "string",
  "date_of_birth": "date (YYYY-MM-DD)",
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601) | null"
}
```

### Note

```json
{
  "id": "integer",
  "patient_id": "integer",
  "content": "string",
  "note_timestamp": "datetime (ISO 8601)",
  "created_at": "datetime (ISO 8601)"
}
```

### Summary

```json
{
  "heading": {
    "name": "string",
    "age": "integer",
    "mrn": "string"
  },
  "summary": "string",
  "note_count": "integer"
}
```

---

## Rate Limiting

Currently no rate limiting is enforced. Future versions will implement:
- 100 requests/minute for standard endpoints
- 10 requests/minute for AI summary generation
- Rate limit headers in responses

---

## Versioning

API versioning is handled via URL path: `/api/v1/`

Breaking changes will increment the major version (v2, v3, etc.).

---

## Interactive Documentation

FastAPI provides auto-generated interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

---

## Usage Examples

### cURL Examples

**Create a patient:**
```bash
curl -X POST http://localhost:8000/api/v1/patients \
  -H "Content-Type: application/json" \
  -d '{"name": "John Smith", "date_of_birth": "1985-03-15"}'
```

**List patients with search:**
```bash
curl "http://localhost:8000/api/v1/patients?search=john&sort_by=name"
```

**Add a note:**
```bash
curl -X POST http://localhost:8000/api/v1/patients/1/notes \
  -H "Content-Type: application/json" \
  -d '{
    "content": "S: Patient reports improvement...",
    "note_timestamp": "2024-01-20T10:00:00"
  }'
```

**Generate summary (sync):**
```bash
curl "http://localhost:8000/api/v1/patients/1/summary?audience=clinician"
```

**Generate summary (async):**
```bash
# Start job
curl -X POST "http://localhost:8000/api/v1/patients/1/summary/async"

# Poll for result
curl "http://localhost:8000/api/v1/patients/1/summary/jobs/{job_id}"
```

### Python Examples

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Create patient
response = requests.post(f"{BASE_URL}/patients", json={
    "name": "Jane Doe",
    "date_of_birth": "1990-07-22"
})
patient = response.json()

# Add note
requests.post(f"{BASE_URL}/patients/{patient['id']}/notes", json={
    "content": "SOAP Note content...",
    "note_timestamp": "2024-01-20T10:00:00"
})

# Generate summary (async)
job = requests.post(f"{BASE_URL}/patients/{patient['id']}/summary/async").json()

# Poll until complete
import time
while True:
    status = requests.get(
        f"{BASE_URL}/patients/{patient['id']}/summary/jobs/{job['job_id']}"
    ).json()
    if status["status"] == "completed":
        print(status["result"]["summary"])
        break
    time.sleep(2)
```

---

## Contact

For API support or questions, contact the development team.
