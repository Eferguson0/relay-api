from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class GoalWeight(Base):
    __tablename__ = "goal_weight"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("auth_users.id"), nullable=False)
    date_hour = Column(
        DateTime(timezone=True), nullable=False
    )  # Hour for the goal targets
    weight = Column(Numeric, nullable=True)  # Target weight in kg or lbs
    body_fat_percentage = Column(Numeric, nullable=True)  # Target body fat percentage
    muscle_mass_percentage = Column(
        Numeric, nullable=True
    )  # Target muscle mass percentage
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Unique constraint to ensure one goal per user per hour
    __table_args__ = (UniqueConstraint("user_id", "date_hour"),)

    # Relationships
    user = relationship("AuthUser")
