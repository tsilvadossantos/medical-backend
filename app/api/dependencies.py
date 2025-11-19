"""
API dependencies module.

Provides common dependencies for API endpoints.
"""
from sqlalchemy.orm import Session
from app.db.session import get_db

__all__ = ["get_db"]
