from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class GoalGeneral(Base):
    __tablename__ = "goal_general"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("auth_users.id"), nullable=False)
    goal_description = Column(Text, nullable=False)  # Description of the general goal
    target_date = Column(DateTime(timezone=True), nullable=True)  # Optional target date
    # Weight-related goal fields
    target_weight = Column(Numeric, nullable=True)  # Target weight in kg or lbs
    target_body_fat_percentage = Column(
        Numeric, nullable=True
    )  # Target body fat percentage
    target_muscle_mass_percentage = Column(
        Numeric, nullable=True
    )  # Target muscle mass percentage
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Unique constraint to ensure one goal per user
    __table_args__ = (UniqueConstraint("user_id"),)

    # Relationships
    user = relationship("AuthUser")
