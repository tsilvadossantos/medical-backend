# Medical Backend API

A FastAPI backend for managing patient medical records and generating summaries from SOAP notes.

## Features

- Patient CRUD operations with pagination and search
- Medical note management with timestamps
- AI-powered patient summary generation ([configurable providers](PROVIDERS.md))
- Async job processing with Redis and Celery
- Environment-specific configurations (dev/staging/prod)
- Prometheus metrics for monitoring
- CI/CD with GitHub Actions
- 80%+ test coverage
- Fully containerized with Docker

### Design Decisions & Trade-offs

This project prioritizes **simplicity, ease of setup, and maintainability** over enterprise-scale features. The following were intentionally deferred:

| Not Implemented | Rationale | Future Consideration |
|-----------------|-----------|----------------------|
| **Authentication/Authorization** | Keeps setup simple; auth requirements vary by deployment context | Add JWT/OAuth2 when deploying to production with user-facing access |
| **Distributed Tracing** | Prometheus metrics sufficient for single-service debugging | Add OpenTelemetry when scaling to multiple services |
| **Circuit Breakers** | LLM fallback to rule-based extraction handles failures adequately | Add resilience4j patterns for high-throughput production |
| **Response Caching** | Summaries are patient-specific and change with new notes | Add Redis caching for frequently-accessed summaries if latency becomes critical |
| **Kubernetes Manifests** | Docker Compose sufficient for local dev and small deployments | Add K8s when horizontal scaling or multi-region deployment required |
| **Audit Logging** | Basic logging covers debugging needs | Add structured audit trail for HIPAA compliance in production |
| **Rate Limiting per User** | No auth means no user context for limits | Add when authentication is implemented |
| **Code Formatting (Black/isort)** | CI pipeline defines linting rules; code follows conventions but not auto-formatted | Run `black app/ --line-length=120` and `isort app/` before committing |

**Design Philosophy**: Build what's needed, not what might be needed. These features can be added incrementally as requirements evolve, without requiring architectural changes—the layered design supports this extensibility.

## Quick Start

### One Command Setup (Recommended)

```bash
cd medical-backend
./scripts/init.sh
```

This automatically:
- Creates `.env` configuration
- Builds and starts all services
- Waits for services to be healthy
- Pulls the Ollama model
- API ready at http://localhost:8000

### Management Scripts

All scripts run from the `medical-backend` directory:

| Script | Description |
|--------|-------------|
| `./scripts/init.sh` | Full automated setup (single command) |
| `./scripts/start.sh` | Start services in background |
| `./scripts/stop.sh` | Stop all services |
| `./scripts/restart.sh` | Restart all services |
| `./scripts/status.sh` | Check service health |
| `./scripts/logs.sh [service]` | View logs |
| `./scripts/test.sh` | Run tests with coverage |
| `./scripts/test-quick.sh` | Run tests without coverage |
| `./scripts/shell.sh [service]` | Open shell in container |
| `./scripts/db-reset.sh` | Reset database |
| `./scripts/purge.sh` | Remove all data and volumes |

### Local Development

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API Endpoints

### Health & Monitoring
- `GET /health` - Returns `{"status": "ok"}`
- `GET /metrics` - Prometheus metrics

### Patients
- `GET /api/v1/patients` - List patients (supports `page`, `size`, `sort_by`, `sort_order`, `search`)
- `GET /api/v1/patients/{id}` - Get patient by ID
- `POST /api/v1/patients` - Create patient
- `PUT /api/v1/patients/{id}` - Update patient
- `DELETE /api/v1/patients/{id}` - Delete patient

### Notes
- `GET /api/v1/patients/{id}/notes` - List patient notes
- `POST /api/v1/patients/{id}/notes` - Create note
- `DELETE /api/v1/patients/{id}/notes/{note_id}` - Delete specific note
- `DELETE /api/v1/patients/{id}/notes` - Delete all patient notes

### Summary
- `GET /api/v1/patients/{id}/summary` - Generate summary (sync)
- `POST /api/v1/patients/{id}/summary/async` - Queue async summary (returns job_id)
- `GET /api/v1/patients/{id}/summary/jobs/{job_id}` - Get job status/result

## Example Usage

### Automated Test Client

Run the comprehensive test script that exercises all API features:

```bash
./scripts/test-client.sh
```

This tests: health checks, patient CRUD, pagination, sorting, search, notes, sync/async summaries, and error handling.

**Requires:** `jq` (`brew install jq` or `apt-get install jq`)

### Manual cURL Examples

```bash
# Create patient
curl -X POST http://localhost:8000/api/v1/patients \
  -H "Content-Type: application/json" \
  -d '{"name": "John Smith", "date_of_birth": "1985-03-15"}'

# Add note
curl -X POST http://localhost:8000/api/v1/patients/1/notes \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Subjective: Patient reports...",
    "note_timestamp": "2024-01-15T10:30:00Z"
  }'

# Get summary (sync)
curl http://localhost:8000/api/v1/patients/1/summary

# Queue async summary
curl -X POST http://localhost:8000/api/v1/patients/1/summary/async

# Check job status
curl http://localhost:8000/api/v1/patients/1/summary/jobs/{job_id}

# Get Prometheus metrics
curl http://localhost:8000/metrics
```

## Environment Configuration

The application supports multiple environments with automatic configuration loading:

| Environment | Config File | Description |
|-------------|-------------|-------------|
| development | `.env.development` | Local development with debug enabled |
| staging | `.env.staging` | Pre-production testing |
| production | `.env.production` | Production with strict security |
| testing | `.env.test` | Automated testing |

Set the environment with:
```bash
export APP_ENV=production
```

### Environment-Specific Features

| Feature | Development | Staging | Production |
|---------|-------------|---------|------------|
| Debug Mode | ✅ | ❌ | ❌ |
| Log Level | DEBUG | INFO | WARNING |
| CORS Origins | * | Configured | Strict |
| DB Pool Size | 3 | 10 | 20 |
| Rate Limiting | Relaxed | Normal | Strict |
| API Docs | ✅ | ✅ | ❌ |

## CI/CD Pipeline

The project includes GitHub Actions for automated testing:

### Workflow Features
- **Linting**: Black, flake8, isort, mypy
- **Unit Tests**: With 80% coverage requirement
- **Integration Tests**: With PostgreSQL and Redis services
- **Docker Build**: On main branch pushes

### Running CI Locally

```bash
# Format code
black app/

# Check imports
isort app/

# Lint
flake8 app/ --max-line-length=120

# Type check
mypy app/ --ignore-missing-imports

# Run tests
pytest app/tests/ -v --cov=app --cov-fail-under=80
```

## Prometheus Monitoring

The application exposes Prometheus metrics at `/metrics`:

### Available Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `http_requests_total` | Counter | Total HTTP requests by method/endpoint/status |
| `http_request_duration_seconds` | Histogram | Request latency |
| `http_requests_in_progress` | Gauge | Currently processing requests |
| `patients_created_total` | Counter | Patients created |
| `notes_created_total` | Counter | Notes created |
| `summary_requests_total` | Counter | Summary generations |
| `summary_generation_duration_seconds` | Histogram | Summary generation time |
| `llm_requests_total` | Counter | LLM provider calls |
| `celery_tasks_total` | Counter | Celery task executions |
| `health_check_status` | Gauge | Component health (1=healthy) |

### Example Prometheus Configuration

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'medical-backend'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

## Testing

```bash
# Run with coverage (requires 80% minimum)
./scripts/test.sh

# Quick run without coverage
./scripts/test-quick.sh

# Run specific test
pytest app/tests/test_patients.py -v

# Run with parallel execution
pytest app/tests/ -n auto

# Run integration tests only
pytest app/tests/integration/ -v
```

Coverage report: `htmlcov/index.html`

## Project Structure

```
medical-backend/
├── .github/workflows/   # CI/CD pipelines
├── app/
│   ├── api/v1/          # API endpoints
│   ├── core/            # Configuration & metrics
│   ├── db/              # Database setup
│   ├── middleware/      # Custom middleware
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── repositories/    # Data access layer
│   ├── services/        # Business logic
│   ├── utils/           # Utilities
│   ├── worker/          # Celery tasks
│   ├── providers/       # LLM provider integrations
│   └── tests/           # Test files
│       └── integration/ # Integration tests
├── scripts/             # Management scripts
├── docker/              # Docker files
├── sample_notes/        # Example SOAP notes
├── docker-compose.yml
├── pyproject.toml       # Linting configuration
└── requirements.txt
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| APP_ENV | Environment (development/staging/production) | development |
| DATABASE_URL | PostgreSQL connection string | postgresql://postgres:postgres@db:5432/medical_db |
| DB_POOL_SIZE | Database connection pool size | 5 |
| REDIS_URL | Redis connection string | redis://redis:6379/0 |
| LLM_PROVIDER | LLM provider (ollama/openai/anthropic) | ollama |
| OLLAMA_URL | Ollama service URL | http://ollama:11434 |
| OLLAMA_MODEL | Ollama model name | llama3.2 |
| OPENAI_API_KEY | OpenAI API key | None |
| OPENAI_MODEL | OpenAI model name | gpt-3.5-turbo |
| ANTHROPIC_API_KEY | Anthropic API key | None |
| ANTHROPIC_MODEL | Anthropic model name | claude-3-haiku-20240307 |
| LOG_LEVEL | Logging level | INFO |
| CORS_ORIGINS | Allowed CORS origins | * |
| SECRET_KEY | Application secret key | dev-secret-key |
| METRICS_ENABLED | Enable Prometheus metrics | true |

## LLM Providers

The system is **GenAI-agnostic** with pluggable providers:

| Provider | Cost | Setup |
|----------|------|-------|
| **Ollama** (default) | Free | Bundled in Docker or external |
| **OpenAI** | Paid | Requires API key |
| **Anthropic** | Paid | Requires API key |

### Ollama Options

**Bundled (default)** - Ollama runs as a Docker container:
```bash
# .env
OLLAMA_URL=http://ollama:11434
```

**External (shared/production)** - Use existing Ollama instance:
```bash
# .env - Mac/Windows
OLLAMA_URL=http://host.docker.internal:11434

# .env - Linux or remote server
OLLAMA_URL=http://192.168.1.100:11434
```

The scripts auto-detect which mode based on `OLLAMA_URL`.

### Switch Providers

Edit `.env`:

```bash
# Ollama (default - free)
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2

# OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...

# Anthropic
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

Falls back to rule-based extraction if LLM unavailable.

### Async Processing

For non-blocking summary generation:

1. `POST /api/v1/patients/{id}/summary/async` → returns `job_id`
2. `GET /api/v1/patients/{id}/summary/jobs/{job_id}` → poll for result

Statuses: `pending` → `processing` → `completed` (or `failed`)

## Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **API Contract:** [API_CONTRACT.md](API_CONTRACT.md)
- **System Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **LLM Providers:** [PROVIDERS.md](PROVIDERS.md)
