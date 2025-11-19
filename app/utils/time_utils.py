"""
Time utilities module.

Provides helper functions for time and date operations.
"""
from datetime import datetime, timezone


def utc_now() -> datetime:
    """
    Get current UTC datetime.

    Returns:
        Current datetime in UTC timezone
    """
    return datetime.now(timezone.utc)


def format_timestamp(dt: datetime) -> str:
    """
    Format datetime as ISO 8601 string.

    Parameters:
        dt: Datetime object to format

    Returns:
        ISO 8601 formatted string
    """
    return dt.isoformat()
