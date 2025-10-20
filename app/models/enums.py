from enum import Enum


class DataSource(str, Enum):
    """Enum for data source types"""

    APPLE_WATCH = "apple_watch"
    FITBIT = "fitbit"
    GARMIN = "garmin"
    SAMSUNG = "samsung"
    GOOGLE_FIT = "google_fit"
    STRAVA = "strava"
    MANUAL = "manual"
    OTHER = "other"
