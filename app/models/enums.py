from enum import Enum


class DataSource(str, Enum):
    """Enum for data source types"""

    APPLE_WATCH = "Apple Watch"
    FITBIT = "Fitbit"
    GARMIN = "Garmin"
    SAMSUNG = "Samsung"
    GOOGLE_FIT = "Google Fit"
    STRAVA = "Strava"
    MANUAL = "Manual"
    OTHER = "Other"
