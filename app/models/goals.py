from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class GoalWeight(Base):
    __tablename__ = "goal_weight"

    user_email = Column(
        String, ForeignKey("users.email"), primary_key=True, nullable=False
    )
    weight = Column(Numeric, nullable=True)  # Target weight in kg or lbs
    body_fat_percentage = Column(Numeric, nullable=True)  # Target body fat percentage
    muscle_mass_percentage = Column(
        Numeric, nullable=True
    )  # Target muscle mass percentage
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")


class GoalDailyDiet(Base):
    __tablename__ = "goal_daily_diet"

    user_email = Column(
        String, ForeignKey("users.email"), primary_key=True, nullable=False
    )
    calories = Column(Numeric, nullable=True)  # Target daily calories
    protein = Column(Numeric, nullable=True)  # Target daily protein in grams
    carbs = Column(Numeric, nullable=True)  # Target daily carbs in grams
    fat = Column(Numeric, nullable=True)  # Target daily fat in grams
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")


class GoalMessage(Base):
    __tablename__ = "goal_message"

    user_email = Column(
        String, ForeignKey("users.email"), primary_key=True, nullable=False
    )
    goal_message = Column(Text, nullable=False)  # Goal message/description
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")
