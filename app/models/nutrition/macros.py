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


class NutritionMacros(Base):
    __tablename__ = "nutrition_macros"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("auth_users.id"), nullable=False)
    datetime = Column(DateTime(timezone=True), nullable=False)
    protein = Column(Numeric, nullable=True)  # grams
    carbs = Column(Numeric, nullable=True)  # grams
    fat = Column(Numeric, nullable=True)  # grams
    calories = Column(Numeric, nullable=True)  # kcal
    meal_name = Column(
        String, nullable=True
    )  # e.g., "Breakfast", "Lunch", "Dinner", "Snack"
    notes = Column(Text, nullable=True)  # Additional notes about the meal
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("AuthUser")
