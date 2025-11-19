"""
Logging configuration module.

Sets up structured logging for the application with configurable log levels.
"""
import logging
import sys
from app.core.settings import settings


def setup_logging():
    """
    Configure application logging with appropriate formatters and handlers.

    Sets up console logging with timestamp, level, and message formatting.
    Log level is determined by the LOG_LEVEL environment variable.
    """
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )

    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)


logger = logging.getLogger(__name__)
