"""Utility functions for datetime parsing and formatting."""

from datetime import datetime, timezone


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


def get_day_boundaries_from_datetime(datetime_str: str) -> tuple[datetime, datetime]:
    """
    Parse an ISO datetime string and return UTC day boundaries for that date.
    
    Handles both ISO datetime strings (with timezone) and date strings (YYYY-MM-DD).
    For date strings, assumes UTC timezone.
    
    Args:
        datetime_str: ISO datetime string (e.g., "2025-11-06T22:23:22Z") 
                      or date string (e.g., "2025-11-06")
    
    Returns:
        Tuple of (start_of_day_utc, end_of_day_utc) as timezone-aware datetimes
        
    Example:
        >>> start, end = get_day_boundaries_from_datetime("2025-11-06T22:23:22Z")
        >>> # Returns UTC boundaries for Nov 6, 2025
    """
    # Try parsing as ISO datetime first
    try:
        parsed = parse_iso_datetime(datetime_str)
    except ValueError:
        # Fall back to date-only format (assume UTC)
        date_obj = datetime.strptime(datetime_str, "%Y-%m-%d").date()
        parsed = datetime.combine(date_obj, datetime.min.time(), tzinfo=timezone.utc)
    
    # Get the date in the parsed datetime's timezone
    user_tz = parsed.tzinfo or timezone.utc
    date_in_user_tz = parsed.date()
    
    # Create start and end of day in user's timezone
    start_of_day = datetime.combine(date_in_user_tz, datetime.min.time(), tzinfo=user_tz)
    end_of_day = datetime.combine(date_in_user_tz, datetime.max.time(), tzinfo=user_tz)
    
    # Convert to UTC for database queries
    start_utc = start_of_day.astimezone(timezone.utc)
    end_utc = end_of_day.astimezone(timezone.utc)
    
    return start_utc, end_utc

