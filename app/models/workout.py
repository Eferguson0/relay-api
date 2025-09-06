from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    PrimaryKeyConstraint,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class ActiveCalories(Base):
    __tablename__ = "active_calories"

    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    date = Column(
        DateTime(timezone=True), nullable=False
    )  # Store full datetime for hourly data
    calories_burned = Column(Numeric, nullable=True)  # Calories burned in this hour
    source = Column(
        Text, nullable=False
    )  # Source of the data (e.g., "Apple Watch", "Fitbit")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Primary key constraint and check constraints
    __table_args__ = (PrimaryKeyConstraint("user_id", "date", "source"),)

    # Relationships
    user = relationship("User")


class HourlySteps(Base):
    __tablename__ = "hourly_steps"

    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    date = Column(
        DateTime(timezone=True), nullable=False
    )  # Store full datetime for hourly data
    steps = Column(Integer, nullable=True)  # Steps taken in this hour
    source = Column(
        Text, nullable=False
    )  # Source of the data (e.g., "Apple Watch", "Fitbit")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Primary key constraint and check constraints
    __table_args__ = (PrimaryKeyConstraint("user_id", "date", "source"),)

    # Relationships
    user = relationship("User")
