from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base
from app.models.enums import DataSource


class ActivityMiles(Base):
    __tablename__ = "activity_miles"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("auth_users.id"), nullable=False)
    date_hour = Column(
        DateTime(timezone=True), nullable=False
    )  # Store full datetime for hourly data
    miles = Column(Numeric, nullable=True)  # Miles traveled in this hour
    activity_type = Column(
        String, nullable=True
    )  # e.g., "walking", "running", "cycling"
    source = Column(
        Enum(DataSource), nullable=False
    )  # Source of the data (e.g., "Apple Watch", "Fitbit")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Unique constraint to ensure one record per user per date per source
    __table_args__ = (UniqueConstraint("user_id", "date_hour", "source"),)

    # Relationships
    user = relationship("AuthUser")
