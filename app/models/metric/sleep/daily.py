from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base
from app.models.enums import DataSource


class SleepDaily(Base):
    __tablename__ = "sleep_daily"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("auth_users.id"), nullable=False)
    date_day = Column(
        DateTime(timezone=True), nullable=False
    )  # Date of sleep (start of sleep day)
    bedtime = Column(DateTime(timezone=True), nullable=True)  # When user went to bed
    wake_time = Column(DateTime(timezone=True), nullable=True)  # When user woke up
    total_sleep_minutes = Column(
        Integer, nullable=True
    )  # Total sleep duration in minutes
    deep_sleep_minutes = Column(
        Integer, nullable=True
    )  # Deep sleep duration in minutes
    light_sleep_minutes = Column(
        Integer, nullable=True
    )  # Light sleep duration in minutes
    rem_sleep_minutes = Column(Integer, nullable=True)  # REM sleep duration in minutes
    awake_minutes = Column(Integer, nullable=True)  # Time awake during sleep period
    sleep_efficiency = Column(Numeric, nullable=True)  # Sleep efficiency percentage
    sleep_quality_score = Column(Integer, nullable=True)  # Sleep quality score (1-10)
    source = Column(
        Enum(DataSource), nullable=False
    )  # Source of the data (e.g., "Apple Watch", "Fitbit")
    notes = Column(Text, nullable=True)  # Additional notes about sleep
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Unique constraint to ensure one record per user per sleep date per source
    __table_args__ = (UniqueConstraint("user_id", "date_day", "source"),)

    # Relationships
    user = relationship("AuthUser")
