"""
Prometheus metrics definitions.

Defines all application metrics for monitoring and observability.
"""
from prometheus_client import Counter, Histogram, Gauge, Info

# Application info
APP_INFO = Info('medical_backend', 'Medical Backend application information')

# HTTP Request metrics
HTTP_REQUESTS_TOTAL = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code']
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

HTTP_REQUESTS_IN_PROGRESS = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests currently being processed',
    ['method', 'endpoint']
)

# Patient metrics
PATIENTS_CREATED_TOTAL = Counter(
    'patients_created_total',
    'Total number of patients created'
)

PATIENTS_UPDATED_TOTAL = Counter(
    'patients_updated_total',
    'Total number of patients updated'
)

PATIENTS_DELETED_TOTAL = Counter(
    'patients_deleted_total',
    'Total number of patients deleted'
)

PATIENTS_TOTAL = Gauge(
    'patients_total',
    'Total number of patients in the system'
)

# Notes metrics
NOTES_CREATED_TOTAL = Counter(
    'notes_created_total',
    'Total number of notes created'
)

NOTES_DELETED_TOTAL = Counter(
    'notes_deleted_total',
    'Total number of notes deleted'
)

# Summary generation metrics
SUMMARY_REQUESTS_TOTAL = Counter(
    'summary_requests_total',
    'Total number of summary generation requests',
    ['audience', 'mode']  # mode: sync or async
)

SUMMARY_GENERATION_DURATION_SECONDS = Histogram(
    'summary_generation_duration_seconds',
    'Summary generation duration in seconds',
    ['provider'],
    buckets=[0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0]
)

SUMMARY_GENERATION_ERRORS_TOTAL = Counter(
    'summary_generation_errors_total',
    'Total number of summary generation errors',
    ['provider', 'error_type']
)

# LLM Provider metrics
LLM_REQUESTS_TOTAL = Counter(
    'llm_requests_total',
    'Total number of LLM provider requests',
    ['provider']
)

LLM_REQUEST_DURATION_SECONDS = Histogram(
    'llm_request_duration_seconds',
    'LLM request duration in seconds',
    ['provider'],
    buckets=[0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0]
)

LLM_ERRORS_TOTAL = Counter(
    'llm_errors_total',
    'Total number of LLM provider errors',
    ['provider', 'error_type']
)

# Celery job queue metrics
CELERY_TASKS_TOTAL = Counter(
    'celery_tasks_total',
    'Total number of Celery tasks',
    ['task_name', 'status']  # status: queued, started, succeeded, failed
)

CELERY_TASK_DURATION_SECONDS = Histogram(
    'celery_task_duration_seconds',
    'Celery task duration in seconds',
    ['task_name'],
    buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 300.0]
)

CELERY_TASKS_IN_QUEUE = Gauge(
    'celery_tasks_in_queue',
    'Number of tasks currently in the Celery queue'
)

# Database metrics
DB_CONNECTIONS_TOTAL = Gauge(
    'db_connections_total',
    'Total number of database connections in pool'
)

DB_CONNECTIONS_IN_USE = Gauge(
    'db_connections_in_use',
    'Number of database connections currently in use'
)

DB_QUERY_DURATION_SECONDS = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation'],  # operation: select, insert, update, delete
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
)

# Error metrics
ERRORS_TOTAL = Counter(
    'errors_total',
    'Total number of errors',
    ['error_type', 'endpoint']
)

# Health metrics
HEALTH_CHECK_STATUS = Gauge(
    'health_check_status',
    'Health check status (1 = healthy, 0 = unhealthy)',
    ['component']  # component: app, database, redis, llm
)


def init_app_info(version: str, environment: str):
    """
    Initialize application info metric.

    Args:
        version: Application version
        environment: Current environment (development, staging, production)
    """
    APP_INFO.info({
        'version': version,
        'environment': environment
    })
