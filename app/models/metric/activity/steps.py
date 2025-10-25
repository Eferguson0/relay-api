from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base
from app.models.enums import DataSource


class ActivitySteps(Base):
    __tablename__ = "activity_steps"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("auth_users.id"), nullable=False)
    date_hour = Column(
        DateTime(timezone=True), nullable=False
    )  # Store full datetime for hourly data
    steps = Column(Integer, nullable=True)  # Steps taken in this hour
    source = Column(
        Enum(DataSource), nullable=False
    )  # Source of the data (e.g., "apple_watch", "fitbit")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Unique constraint to ensure one record per user per date per source
    __table_args__ = (UniqueConstraint("user_id", "date_hour", "source"),)

    # Relationships
    user = relationship("AuthUser")
