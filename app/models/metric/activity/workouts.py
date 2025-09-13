from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base
from app.models.enums import DataSource


class ActivityWorkouts(Base):
    __tablename__ = "activity_workouts"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("auth_users.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    workout_name = Column(
        String, nullable=True
    )  # e.g., "Morning Run", "Weight Training"
    workout_type = Column(
        String, nullable=False
    )  # e.g., "cardio", "strength", "flexibility"
    source = Column(
        Enum(DataSource), nullable=False
    )  # Source of the data (e.g., "Apple Watch", "Manual")
    duration_minutes = Column(Integer, nullable=True)  # Duration in minutes
    calories_burned = Column(Numeric, nullable=True)  # Calories burned during workout
    distance_miles = Column(Numeric, nullable=True)  # Distance covered in miles
    avg_heart_rate = Column(Integer, nullable=True)  # Average heart rate during workout
    max_heart_rate = Column(Integer, nullable=True)  # Maximum heart rate during workout
    intensity = Column(String, nullable=True)  # low, moderate, high
    source = Column(
        Enum(DataSource), nullable=True
    )  # Source of the data (e.g., "Apple Watch", "Manual")
    notes = Column(String, nullable=True)  # Additional notes about the workout
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Unique constraint to prevent duplicate workouts from same source
    __table_args__ = (UniqueConstraint("user_id", "date", "source"),)

    # Relationships
    user = relationship("AuthUser")
