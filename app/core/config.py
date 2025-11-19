"""
Configuration module for application-wide constants and settings.

Provides centralized access to configuration values used throughout the application.
"""
from app.core.settings import settings

DATABASE_URL = settings.DATABASE_URL
OPENAI_API_KEY = settings.OPENAI_API_KEY
APP_ENV = settings.APP_ENV
LOG_LEVEL = settings.LOG_LEVEL
