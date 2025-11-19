# System Design Architecture

## Overview

The Medical Backend is a cloud-native, microservices-inspired application designed for managing patient medical records and generating AI-powered summaries from SOAP notes. The system follows a layered architecture with clear separation of concerns, enabling scalability, maintainability, and testability.

---

## High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  Web Browser  │  Mobile App  │  API Client  │  Prometheus  │  CI/CD Runner  │
└───────┬───────┴──────┬───────┴──────┬───────┴──────┬───────┴───────┬────────┘
        │              │              │              │               │
        ▼              ▼              ▼              ▼               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           API GATEWAY LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                         FastAPI Application                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │    CORS     │  │   Metrics   │  │   Logging   │  │  Exception  │         │
│  │ Middleware  │  │ Middleware  │  │ Middleware  │  │   Handler   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘         │
└───────┬─────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            API LAYER (v1)                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐  │
│  │  Health   │  │ Patients  │  │   Notes   │  │  Summary  │  │  Metrics  │  │
│  │ Endpoint  │  │ Endpoints │  │ Endpoints │  │ Endpoints │  │ Endpoint  │  │
│  └───────────┘  └───────────┘  └───────────┘  └─────┬─────┘  └───────────┘  │
└───────┬─────────────────┬─────────────┬─────────────┼────────────────────────┘
        │                 │             │             │
        ▼                 ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SERVICE LAYER                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │ PatientService  │  │  NoteService    │  │ SummaryService  │              │
│  │                 │  │                 │  │                 │              │
│  │ • CRUD logic    │  │ • CRUD logic    │  │ • LLM calls     │              │
│  │ • Validation    │  │ • Patient check │  │ • Note parsing  │              │
│  │ • Pagination    │  │ • Timestamps    │  │ • Age calc      │              │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘              │
└───────────┼────────────────────┼────────────────────┼────────────────────────┘
            │                    │                    │
            ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        REPOSITORY LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐              ┌─────────────────────┐               │
│  │  PatientRepository  │              │   NoteRepository    │               │
│  │                     │              │                     │               │
│  │ • get_all (paginate)│              │ • get_by_patient_id │               │
│  │ • get_by_id         │              │ • get_by_id         │               │
│  │ • create            │              │ • create            │               │
│  │ • update            │              │ • delete            │               │
│  │ • delete            │              │ • delete_by_patient │               │
│  │ • search (fuzzy)    │              │                     │               │
│  └──────────┬──────────┘              └──────────┬──────────┘               │
└─────────────┼────────────────────────────────────┼───────────────────────────┘
              │                                    │
              ▼                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      SQLAlchemy ORM                                  │    │
│  │  ┌─────────────────┐              ┌─────────────────┐               │    │
│  │  │  Patient Model  │◄────────────►│   Note Model    │               │    │
│  │  │                 │  1:N         │                 │               │    │
│  │  │ • id            │              │ • id            │               │    │
│  │  │ • name          │              │ • patient_id    │               │    │
│  │  │ • date_of_birth │              │ • content       │               │    │
│  │  │ • created_at    │              │ • note_timestamp│               │    │
│  │  │ • updated_at    │              │ • created_at    │               │    │
│  │  └─────────────────┘              └─────────────────┘               │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│                        ┌─────────────────────┐                               │
│                        │    PostgreSQL 15    │                               │
│                        │   (medical_db)      │                               │
│                        └─────────────────────┘                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                     ASYNC PROCESSING LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────────────────┐      │
│  │   FastAPI   │─────►│    Redis    │◄─────│    Celery Worker       │      │
│  │  (Producer) │ push │   (Broker)  │ poll │                        │      │
│  └─────────────┘      └─────────────┘      │ • generate_summary_task│      │
│                              │             │ • Retries & timeouts   │      │
│                              │             └───────────┬─────────────┘      │
│                              │                         │                    │
│                              ▼                         │                    │
│                       ┌─────────────┐                  │                    │
│                       │    Redis    │◄─────────────────┘                    │
│                       │  (Backend)  │  store results                        │
│                       └─────────────┘                                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                      LLM PROVIDER LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    Provider Factory                                  │    │
│  │                   (get_llm_provider)                                 │    │
│  └────────────────────────────┬────────────────────────────────────────┘    │
│                               │                                              │
│              ┌────────────────┼────────────────┐                             │
│              ▼                ▼                ▼                             │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐                │
│  │ OllamaProvider  │ │ OpenAIProvider  │ │AnthropicProvider│                │
│  │                 │ │                 │ │                 │                │
│  │ • Local/Docker  │ │ • Cloud API     │ │ • Cloud API     │                │
│  │ • Free          │ │ • Paid          │ │ • Paid          │                │
│  │ • llama3.2      │ │ • gpt-3.5/4     │ │ • claude-3      │                │
│  └────────┬────────┘ └────────┬────────┘ └────────┬────────┘                │
│           │                   │                   │                         │
│           ▼                   ▼                   ▼                         │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐                │
│  │  Ollama Server  │ │   OpenAI API    │ │  Anthropic API  │                │
│  │  (localhost/    │ │                 │ │                 │                │
│  │   Docker)       │ │                 │ │                 │                │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                    OBSERVABILITY LAYER                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │   Prometheus    │  │    Logging      │  │  Health Checks  │              │
│  │    Metrics      │  │                 │  │                 │              │
│  │                 │  │ • Request logs  │  │ • /health       │              │
│  │ • HTTP stats    │  │ • Error traces  │  │ • DB connection │              │
│  │ • Business KPIs │  │ • Audit trail   │  │ • Redis ping    │              │
│  │ • LLM latency   │  │                 │  │ • LLM status    │              │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. API Gateway Layer

#### FastAPI Application

**What:** The main entry point for all HTTP requests. FastAPI is an async-capable Python web framework built on Starlette and Pydantic.

**How:**
- Receives HTTP requests and routes them to appropriate endpoints
- Applies middleware chain (CORS → Metrics → Logging)
- Validates request/response data using Pydantic schemas
- Handles exceptions globally and returns standardized errors

**When:**
- On every incoming HTTP request
- At application startup (initializes DB, seeds data, sets up metrics)
- At application shutdown (cleanup)

**Location:** `app/main.py`

---

#### Middleware Components

##### CORS Middleware
**What:** Cross-Origin Resource Sharing configuration for browser security.

**How:** Adds appropriate headers to allow/deny cross-origin requests based on `CORS_ORIGINS` setting.

**When:** Every HTTP request, before routing.

##### Metrics Middleware
**What:** Prometheus instrumentation for HTTP request monitoring.

**How:**
- Records request count, duration, and in-progress gauge
- Normalizes endpoint paths to avoid cardinality explosion
- Skips `/metrics` endpoint to prevent recursion

**When:** Every HTTP request (except `/metrics`), wrapping the entire request lifecycle.

**Location:** `app/middleware/metrics_middleware.py`

##### Logging Middleware
**What:** Request/response logging for audit and debugging.

**How:** Logs method, path, and response status code for every request.

**When:** Every HTTP request.

##### Global Exception Handler
**What:** Catches unhandled exceptions and returns standardized 500 responses.

**How:** Logs full stack trace, returns generic error to client (security).

**When:** Any unhandled exception during request processing.

---

### 2. API Layer

#### Patients Endpoint (`/api/v1/patients`)

**What:** CRUD operations for patient records.

**How:**
- `GET /` - List with pagination, sorting, fuzzy search
- `GET /{id}` - Single patient by ID
- `POST /` - Create new patient
- `PUT /{id}` - Partial update
- `DELETE /{id}` - Remove patient

**When:** Client needs to manage patient records.

**Location:** `app/api/v1/patients.py`

---

#### Notes Endpoint (`/api/v1/patients/{id}/notes`)

**What:** CRUD operations for medical notes attached to patients.

**How:**
- `GET /` - List all notes for a patient
- `POST /` - Create new note with SOAP content
- `DELETE /{note_id}` - Delete specific note
- `DELETE /` - Delete all patient notes

**When:** Client needs to manage medical documentation.

**Location:** `app/api/v1/notes.py`

---

#### Summary Endpoint (`/api/v1/patients/{id}/summary`)

**What:** AI-powered summary generation from patient notes.

**How:**
- `GET /` - Synchronous generation (blocks until complete)
- `POST /async` - Asynchronous generation (returns job ID immediately)
- `GET /jobs/{job_id}` - Poll for async job status/result

**When:**
- Sync: Small datasets, immediate need, low latency tolerance
- Async: Large datasets, background processing, high availability needs

**Location:** `app/api/v1/summary.py`

---

#### Health Endpoint (`/health`)

**What:** Application health check for load balancers and orchestrators.

**How:** Returns `{"status": "ok"}` if application is running.

**When:**
- Container orchestration health probes
- Load balancer health checks
- Monitoring systems

**Location:** `app/api/v1/health.py`

---

#### Metrics Endpoint (`/metrics`)

**What:** Prometheus metrics exposition.

**How:** Returns all collected metrics in Prometheus text format.

**When:** Prometheus scraper polls (typically every 15-30 seconds).

**Location:** `app/api/v1/metrics.py`

---

### 3. Service Layer

#### PatientService

**What:** Business logic for patient operations.

**How:**
- Coordinates between API and Repository layers
- Transforms between Pydantic schemas and ORM models
- Handles pagination metadata calculation
- Validates business rules

**When:** Any patient-related API call.

**Location:** `app/services/patient_service.py`

---

#### NoteService

**What:** Business logic for note operations.

**How:**
- Validates patient existence before note operations
- Coordinates note CRUD operations
- Handles bulk deletion

**When:** Any note-related API call.

**Location:** `app/services/note_service.py`

---

#### SummaryService

**What:** Orchestrates AI summary generation.

**How:**
1. Retrieves patient and all their notes
2. Calculates patient age from date of birth
3. Concatenates and formats note content
4. Calls LLM provider with formatted prompt
5. Returns structured summary response

**When:** Summary generation requested (sync or async).

**Location:** `app/services/summary_service.py`

---

### 4. Repository Layer

#### PatientRepository

**What:** Data access layer for patient table.

**How:**
- Encapsulates SQLAlchemy queries
- Implements pagination with offset/limit
- Implements sorting with dynamic column selection
- Implements fuzzy search with `ILIKE`

**When:** Service layer needs database access.

**Location:** `app/repositories/patient_repository.py`

---

#### NoteRepository

**What:** Data access layer for notes table.

**How:**
- Handles note CRUD operations
- Filters by patient_id for isolation
- Bulk delete operations

**When:** Service layer needs note data access.

**Location:** `app/repositories/note_repository.py`

---

### 5. Data Layer

#### SQLAlchemy ORM Models

**What:** Object-Relational Mapping for database tables.

**How:**
- `Patient`: id, name, date_of_birth, timestamps, notes relationship
- `Note`: id, patient_id (FK), content, note_timestamp, created_at
- Cascade delete: deleting patient removes all notes

**When:** Any database operation.

**Location:** `app/models/patient.py`, `app/models/note.py`

---

#### PostgreSQL Database

**What:** Primary data store for all application data.

**How:**
- Runs as Docker container (postgres:15-alpine)
- Persistent volume for data durability
- Health check via `pg_isready`
- Connection pooling via SQLAlchemy

**When:** Always running when application is up.

**Configuration:**
- Pool size: 3 (dev) / 10 (staging) / 20 (production)
- Max overflow: 5 / 20 / 40
- Connection timeout: 30s / 30s / 60s

---

### 6. Async Processing Layer

#### Redis (Message Broker)

**What:** Message queue for Celery task distribution.

**How:**
- Receives task messages from FastAPI (producer)
- Stores tasks in queue until worker picks them up
- FIFO ordering by default

**When:** Async summary job is created.

**Location:** Docker container (redis:7-alpine)

---

#### Redis (Result Backend)

**What:** Storage for Celery task results.

**How:**
- Workers store task results after completion
- FastAPI queries results for status polling
- Results expire after 1 hour (configurable)

**When:** Task completes (success or failure).

---

#### Celery Worker

**What:** Background task processor.

**How:**
- Polls Redis for new tasks
- Executes `generate_summary_task`
- Stores results back to Redis
- Handles retries and timeouts

**When:** Continuously running, processing tasks as they arrive.

**Configuration:**
- Task time limit: 300 seconds
- Result expiry: 3600 seconds
- Concurrency: Default (based on CPU cores)

**Location:** `app/worker/celery_app.py`, `app/worker/tasks.py`

---

### 7. LLM Provider Layer

#### Provider Factory

**What:** Factory pattern for LLM provider instantiation.

**How:**
- Reads `LLM_PROVIDER` from settings
- Returns appropriate provider instance
- Centralizes provider configuration

**When:** Summary service needs to generate text.

**Location:** `app/providers/factory.py`

---

#### OllamaProvider

**What:** Integration with Ollama local LLM server.

**How:**
- HTTP POST to Ollama API (`/api/generate`)
- Streams response and extracts final text
- Configurable model (default: llama3.2)

**When:** `LLM_PROVIDER=ollama`

**Advantages:** Free, private, no API keys needed
**Disadvantages:** Requires local GPU or slower CPU inference

**Location:** `app/providers/ollama.py`

---

#### OpenAIProvider

**What:** Integration with OpenAI API.

**How:**
- Uses official OpenAI Python client
- Chat completions API
- Configurable model (default: gpt-3.5-turbo)

**When:** `LLM_PROVIDER=openai`

**Advantages:** High quality, fast, reliable
**Disadvantages:** Paid, data leaves your infrastructure

**Location:** `app/providers/openai_provider.py`

---

#### AnthropicProvider

**What:** Integration with Anthropic Claude API.

**How:**
- HTTP POST to Anthropic messages API
- Supports Claude 3 models
- Configurable model (default: claude-3-haiku)

**When:** `LLM_PROVIDER=anthropic`

**Advantages:** High quality, strong reasoning
**Disadvantages:** Paid, data leaves your infrastructure

**Location:** `app/providers/anthropic.py`

---

### 8. Observability Layer

#### Prometheus Metrics

**What:** Time-series metrics for monitoring and alerting.

**How:**
- Counter: Cumulative counts (requests, errors)
- Histogram: Distribution of values (latency, duration)
- Gauge: Current values (in-progress, connections)
- Labels: Dimensions for filtering (method, endpoint, status)

**When:** Collected on every operation, scraped by Prometheus.

**Key Metrics:**
| Metric | Type | Purpose |
|--------|------|---------|
| `http_requests_total` | Counter | Traffic volume, error rates |
| `http_request_duration_seconds` | Histogram | Latency percentiles |
| `summary_generation_duration_seconds` | Histogram | LLM performance |
| `celery_tasks_total` | Counter | Job throughput |

**Location:** `app/core/metrics.py`

---

#### Logging

**What:** Structured application logs for debugging and audit.

**How:**
- Python logging module
- Configurable level per environment
- Request/response logging
- Error stack traces

**When:**
- Every request (INFO)
- Errors (ERROR with stack trace)
- Startup/shutdown (INFO)

**Levels by Environment:**
- Development: DEBUG
- Staging: INFO
- Production: WARNING

**Location:** `app/core/logging_config.py`

---

#### Health Checks

**What:** Liveness and readiness probes for container orchestration.

**How:**
- `/health` endpoint returns 200 if app is running
- Docker health checks for dependent services
- PostgreSQL: `pg_isready`
- Redis: `redis-cli ping`

**When:**
- Container startup (readiness)
- Continuous monitoring (liveness)
- Load balancer routing decisions

---

## Data Flow Examples

### Synchronous Summary Generation

```
Client                FastAPI              SummaryService          LLMProvider           Database
  │                      │                      │                      │                    │
  │  GET /summary        │                      │                      │                    │
  │─────────────────────►│                      │                      │                    │
  │                      │  generate_summary()  │                      │                    │
  │                      │─────────────────────►│                      │                    │
  │                      │                      │  get patient+notes   │                    │
  │                      │                      │─────────────────────────────────────────►│
  │                      │                      │◄─────────────────────────────────────────│
  │                      │                      │                      │                    │
  │                      │                      │  generate_summary()  │                    │
  │                      │                      │─────────────────────►│                    │
  │                      │                      │                      │  HTTP POST         │
  │                      │                      │                      │  to LLM API        │
  │                      │                      │◄─────────────────────│                    │
  │                      │◄─────────────────────│                      │                    │
  │  200 OK + summary    │                      │                      │                    │
  │◄─────────────────────│                      │                      │                    │
```

### Asynchronous Summary Generation

```
Client              FastAPI              Redis              CeleryWorker         LLMProvider
  │                    │                   │                     │                    │
  │ POST /summary/async│                   │                     │                    │
  │───────────────────►│                   │                     │                    │
  │                    │  enqueue task     │                     │                    │
  │                    │──────────────────►│                     │                    │
  │ 202 + job_id       │                   │                     │                    │
  │◄───────────────────│                   │                     │                    │
  │                    │                   │                     │                    │
  │                    │                   │  poll for task      │                    │
  │                    │                   │◄────────────────────│                    │
  │                    │                   │                     │                    │
  │                    │                   │                     │ generate_summary() │
  │                    │                   │                     │───────────────────►│
  │                    │                   │                     │◄───────────────────│
  │                    │                   │                     │                    │
  │                    │                   │  store result       │                    │
  │                    │                   │◄────────────────────│                    │
  │                    │                   │                     │                    │
  │ GET /jobs/{job_id} │                   │                     │                    │
  │───────────────────►│                   │                     │                    │
  │                    │  get result       │                     │                    │
  │                    │──────────────────►│                     │                    │
  │                    │◄──────────────────│                     │                    │
  │ 200 + result       │                   │                     │                    │
  │◄───────────────────│                   │                     │                    │
```

---

## Environment Configuration

### Configuration Loading Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  APP_ENV    │────►│ get_config()│────►│ Config Class│
│ (env var)   │     │             │     │             │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
                    ▼                          ▼                          ▼
           ┌───────────────┐          ┌───────────────┐          ┌───────────────┐
           │ Development   │          │   Staging     │          │  Production   │
           │ Config        │          │   Config      │          │  Config       │
           │               │          │               │          │               │
           │ DEBUG=True    │          │ DEBUG=False   │          │ DEBUG=False   │
           │ LOG=DEBUG     │          │ LOG=INFO      │          │ LOG=WARNING   │
           │ POOL=3        │          │ POOL=10       │          │ POOL=20       │
           └───────┬───────┘          └───────┬───────┘          └───────┬───────┘
                   │                          │                          │
                   ▼                          ▼                          ▼
           ┌───────────────┐          ┌───────────────┐          ┌───────────────┐
           │ .env.         │          │ .env.staging  │          │ .env.         │
           │ development   │          │               │          │ production    │
           └───────────────┘          └───────────────┘          └───────────────┘
```

---

## Deployment Architecture

### Docker Compose Services

```
┌─────────────────────────────────────────────────────────────────┐
│                    Docker Compose Network                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │     app     │  │   worker    │  │   ollama    │              │
│  │  (FastAPI)  │  │  (Celery)   │  │   (LLM)     │              │
│  │             │  │             │  │             │              │
│  │ Port: 8000  │  │ No ports    │  │ Port: 11434 │              │
│  └──────┬──────┘  └──────┬──────┘  └─────────────┘              │
│         │                │                                       │
│         │                │                                       │
│         ▼                ▼                                       │
│  ┌─────────────┐  ┌─────────────┐                               │
│  │     db      │  │    redis    │                               │
│  │ (PostgreSQL)│  │   (Queue)   │                               │
│  │             │  │             │                               │
│  │ Port: 5432  │  │ Port: 6379  │                               │
│  │             │  │             │                               │
│  │ Volume:     │  │ Volume:     │                               │
│  │ postgres_   │  │ redis_data  │                               │
│  │ data        │  │             │                               │
│  └─────────────┘  └─────────────┘                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Service Dependencies

```
         ┌─────────┐
         │   app   │
         └────┬────┘
              │
     ┌────────┼────────┐
     │        │        │
     ▼        ▼        ▼
┌────────┐ ┌────────┐ ┌────────┐
│   db   │ │ redis  │ │ ollama │
└────────┘ └────────┘ └────────┘
     ▲        ▲
     │        │
     └────┬───┘
          │
     ┌────┴────┐
     │ worker  │
     └─────────┘
```

---

## Security Considerations

### Current Implementation

| Layer | Security Measure |
|-------|------------------|
| Network | CORS middleware with configurable origins |
| API | Input validation via Pydantic schemas |
| Database | Parameterized queries (SQLAlchemy ORM) |
| Secrets | Environment variables (not hardcoded) |
| Errors | Generic error messages to clients (no stack traces) |

### Production Recommendations

| Area | Recommendation |
|------|----------------|
| Authentication | Implement JWT or API key auth |
| Rate Limiting | Add per-endpoint rate limits |
| HTTPS | Terminate TLS at load balancer |
| Secrets | Use vault service (HashiCorp Vault, AWS Secrets Manager) |
| Network | Private subnet for database/redis |
| Audit | Enable detailed audit logging |

---

## Scaling Considerations

### Horizontal Scaling

| Component | Strategy |
|-----------|----------|
| FastAPI | Multiple container replicas behind load balancer |
| Celery Workers | Add more worker containers |
| PostgreSQL | Read replicas for queries, primary for writes |
| Redis | Redis Cluster for high availability |
| Ollama | GPU-enabled nodes or external API |

### Vertical Scaling

| Component | Resource | Impact |
|-----------|----------|--------|
| FastAPI | CPU/Memory | More concurrent requests |
| Celery | CPU/Memory | Faster task processing |
| PostgreSQL | Memory | Larger query cache |
| Redis | Memory | Larger queue/result storage |
| Ollama | GPU/VRAM | Faster inference, larger models |

---

## Monitoring & Alerting Recommendations

### Key Alerts

| Metric | Condition | Severity |
|--------|-----------|----------|
| `http_request_duration_seconds` | p99 > 5s | Warning |
| `http_requests_total{status="5xx"}` | Rate > 1/min | Critical |
| `celery_tasks_in_queue` | > 100 | Warning |
| `summary_generation_errors_total` | Rate > 0 | Warning |
| `health_check_status` | = 0 | Critical |

### Dashboard Panels

1. **Request Rate** - Traffic volume over time
2. **Latency Percentiles** - p50, p95, p99 response times
3. **Error Rate** - 4xx and 5xx responses
4. **Task Queue Depth** - Celery backlog
5. **LLM Performance** - Generation time by provider
6. **Database Connections** - Pool utilization

---

## Testing Architecture

### Test Pyramid

```
                    ┌─────────────┐
                    │   E2E Tests │  (Manual/Selenium)
                   ─┴─────────────┴─
                  ┌─────────────────┐
                  │Integration Tests│  (~400 tests)
                 ─┴─────────────────┴─
                ┌───────────────────────┐
                │     Unit Tests        │  (~700 tests)
               ─┴───────────────────────┴─
```

### Test Configuration

| Environment | Database | Redis | LLM |
|-------------|----------|-------|-----|
| Unit Tests | SQLite in-memory | Mocked | Mocked |
| Integration | PostgreSQL (CI service) | Redis (CI service) | Mocked |
| E2E | PostgreSQL (Docker) | Redis (Docker) | Ollama (Docker) |

---

## Future Enhancements

### Short-term
- [ ] Database migrations with Alembic versions
- [ ] JWT authentication
- [ ] Rate limiting middleware
- [ ] Structured JSON logging

### Medium-term
- [ ] GraphQL API option
- [ ] WebSocket for real-time job updates
- [ ] Multi-tenancy support
- [ ] Audit trail table

### Long-term
- [ ] Kubernetes deployment manifests
- [ ] Distributed tracing (OpenTelemetry)
- [ ] ML model versioning
- [ ] Data pipeline for analytics
