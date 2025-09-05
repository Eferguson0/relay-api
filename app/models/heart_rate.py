from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    PrimaryKeyConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class HourlyHeartRate(Base):
    __tablename__ = "hourly_heart_rate"

    user_email = Column(String, ForeignKey("users.email"), nullable=False)
    date = Column(
        DateTime(timezone=True), nullable=False
    )  # Store full datetime for hourly data
    min_hr = Column(Integer)
    avg_hr = Column(Numeric)
    max_hr = Column(Integer)
    source = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Primary key constraint and check constraints
    __table_args__ = (
        PrimaryKeyConstraint("user_email", "date", "source"),
        CheckConstraint(
            "min_hr IS NULL OR (min_hr >= 0 AND min_hr <= 300)",
            name="hourly_heart_rate_min_hr_check",
        ),
        CheckConstraint(
            "avg_hr IS NULL OR (avg_hr >= 0 AND avg_hr <= 300)",
            name="hourly_heart_rate_avg_hr_check",
        ),
        CheckConstraint(
            "max_hr IS NULL OR (max_hr >= 0 AND max_hr <= 300)",
            name="hourly_heart_rate_max_hr_check",
        ),
    )

    # Relationships
    user = relationship("User")
