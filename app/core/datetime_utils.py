"""Utility functions for datetime parsing and formatting."""

from datetime import datetime


def parse_iso_datetime(datetime_str: str) -> datetime:
    """
    Parse an ISO datetime string, handling 'Z' timezone indicator.
    
    Converts 'Z' (UTC) to '+00:00' format for proper ISO parsing.
    
    Args:
        datetime_str: ISO datetime string, optionally ending with 'Z'
        
    Returns:
        Parsed datetime object
        
    Example:
        >>> parse_iso_datetime("2024-01-01T12:00:00Z")
        datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    """
    return datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))

