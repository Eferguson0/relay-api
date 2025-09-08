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


class GoalMacros(Base):
    __tablename__ = "goal_macros"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("auth_users.id"), nullable=False)
    date_hour = Column(
        DateTime(timezone=True), nullable=False
    )  # Hour for the goal targets
    calories = Column(Numeric, nullable=True)  # Target hourly calories
    protein = Column(Numeric, nullable=True)  # Target hourly protein in grams
    carbs = Column(Numeric, nullable=True)  # Target hourly carbs in grams
    fat = Column(Numeric, nullable=True)  # Target hourly fat in grams
    calorie_deficit = Column(
        Numeric, nullable=True
    )  # Calorie deficit target for this hour
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Unique constraint to ensure one goal per user per hour
    __table_args__ = (UniqueConstraint("user_id", "date_hour"),)

    # Relationships
    user = relationship("AuthUser")
