"""
Middleware package.

Contains custom middleware for the application.
"""
from app.middleware.metrics_middleware import MetricsMiddleware

__all__ = ["MetricsMiddleware"]
