# Import all models to ensure they are registered with Base.metadata
# This file is imported by Alembic to discover all models

from .heart_rate import HourlyHeartRate
from .user import User

# This ensures all models are imported and registered with Base.metadata
__all__ = ["User", "HourlyHeartRate"]
