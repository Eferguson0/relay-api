# Import all models to ensure they are registered with Base.metadata
# This file is imported by Alembic to discover all models

from .diet import Diet
from .goals import GoalDailyDiet, GoalMessage, GoalWeight
from .heart_rate import HourlyHeartRate
from .user import User
from .weight import Weight
from .workout import ActiveCalories, HourlySteps

# This ensures all models are imported and registered with Base.metadata
__all__ = [
    "User",
    "HourlyHeartRate",
    "Diet",
    "GoalWeight",
    "GoalDailyDiet",
    "GoalMessage",
    "Weight",
    "ActiveCalories",
    "HourlySteps",
]
