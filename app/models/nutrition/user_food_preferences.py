from sqlalchemy import (
    Column,
    ForeignKey,
    DateTime,
    Numeric,
    String,
    Boolean,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class UserFoodPreference(Base):
    __tablename__ = "food_preferences"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("auth_users.id"), nullable=False)
    food_id = Column(String, ForeignKey("foods.id"), nullable=False)
    is_saved = Column(Boolean, nullable=False, default=False)  # whether the food is saved
    serving_unit = Column(String, nullable=True)  # serving unit of the food
    serving_size = Column(Numeric(10,2), nullable=True, default=1.0)  # serving size of the food
    notes = Column(Text, nullable=True)  # Additional user notes about the food
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("AuthUser")
    food = relationship("Food")

    __table_args__ = (UniqueConstraint("user_id", "food_id", name="uix_user_food"),)