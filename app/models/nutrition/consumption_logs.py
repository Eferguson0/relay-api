from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Boolean,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base



class ConsumptionLog(Base):
    __tablename__ = "consumption_logs"
    __table_args__ = (
        CheckConstraint("servings > 0", name="check_servings_positive"),
        CheckConstraint("calories_total >= 0", name="check_calories_total_non_negative"),
        CheckConstraint("protein_total >= 0", name="check_protein_total_non_negative"),
        CheckConstraint("carbs_total >= 0", name="check_carbs_total_non_negative"),
        CheckConstraint("fat_total >= 0", name="check_fat_total_non_negative"),
    )

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("auth_users.id"), nullable=False, index=True)
    logged_at = Column(DateTime(timezone=True), nullable=False, index=True)
    food_id = Column(String, ForeignKey("foods.id"), nullable=False, index=True)
    servings = Column(Numeric(10,2), nullable=False, default=1.0)  # number of servings of the food
    serving_unit = Column(String, nullable=True, default="serving")  # serving unit of the food; e.g., "slice", "cup", etc.
    calories_total = Column(Numeric(10,2), nullable=False)
    protein_total = Column(Numeric(10,2), nullable=True)
    carbs_total = Column(Numeric(10,2), nullable=True)
    fat_total = Column(Numeric(10,2), nullable=True)
    is_saved = Column(Boolean, nullable=False, default=False, index=True)  # whether the food is saved
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("AuthUser")
    food = relationship("Food", back_populates="logs")