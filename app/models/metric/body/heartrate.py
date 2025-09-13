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


class BodyHeartRate(Base):
    __tablename__ = "body_heartrate"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("auth_users.id"), nullable=False)
    date_hour = Column(
        DateTime(timezone=True), nullable=False
    )  # Store full datetime for hourly data
    heart_rate = Column(Integer, nullable=True)  # Single heart rate reading
    min_hr = Column(Integer, nullable=True)  # Minimum heart rate in this hour
    avg_hr = Column(Numeric, nullable=True)  # Average heart rate in this hour
    max_hr = Column(Integer, nullable=True)  # Maximum heart rate in this hour
    resting_hr = Column(Integer, nullable=True)  # Resting heart rate
    heart_rate_variability = Column(Numeric, nullable=True)  # HRV in milliseconds
    source = Column(Enum(DataSource), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Unique constraint and check constraints
    __table_args__ = (UniqueConstraint("user_id", "date_hour", "source"),)

    # Relationships
    user = relationship("AuthUser")
