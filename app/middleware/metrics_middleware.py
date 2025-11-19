"""
Prometheus metrics middleware.

Automatically instruments HTTP requests with timing and counting metrics.
"""
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.metrics import (
    HTTP_REQUESTS_TOTAL,
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS_IN_PROGRESS,
    ERRORS_TOTAL
)
from app.core.settings import settings


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to collect HTTP request metrics for Prometheus.

    Tracks request count, duration, and in-progress requests.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request and record metrics.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            HTTP response
        """
        # Skip metrics collection if disabled
        if not settings.METRICS_ENABLED:
            return await call_next(request)

        # Skip metrics endpoint itself to avoid recursion
        if request.url.path == "/metrics":
            return await call_next(request)

        method = request.method
        endpoint = self._get_endpoint_label(request.url.path)

        # Track in-progress requests
        HTTP_REQUESTS_IN_PROGRESS.labels(
            method=method,
            endpoint=endpoint
        ).inc()

        start_time = time.time()
        status_code = 500  # Default to error

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response

        except Exception as e:
            # Record error metric
            ERRORS_TOTAL.labels(
                error_type=type(e).__name__,
                endpoint=endpoint
            ).inc()
            raise

        finally:
            # Record request duration
            duration = time.time() - start_time
            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            # Record request count
            HTTP_REQUESTS_TOTAL.labels(
                method=method,
                endpoint=endpoint,
                status_code=str(status_code)
            ).inc()

            # Decrement in-progress counter
            HTTP_REQUESTS_IN_PROGRESS.labels(
                method=method,
                endpoint=endpoint
            ).dec()

    def _get_endpoint_label(self, path: str) -> str:
        """
        Normalize endpoint path for metric labels.

        Replaces dynamic path segments (IDs) with placeholders
        to avoid high cardinality.

        Args:
            path: Request URL path

        Returns:
            Normalized endpoint label
        """
        # Replace numeric IDs with placeholder
        parts = path.split('/')
        normalized = []

        for part in parts:
            if part.isdigit():
                normalized.append('{id}')
            elif self._is_uuid(part):
                normalized.append('{uuid}')
            else:
                normalized.append(part)

        return '/'.join(normalized)

    def _is_uuid(self, value: str) -> bool:
        """
        Check if string looks like a UUID.

        Args:
            value: String to check

        Returns:
            True if value appears to be a UUID
        """
        # Simple UUID check (32 hex chars with optional dashes)
        clean = value.replace('-', '')
        return len(clean) == 32 and all(c in '0123456789abcdef' for c in clean.lower())
