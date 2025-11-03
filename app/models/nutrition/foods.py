from sqlalchemy import (
    Column,
    DateTime,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base



class Food(Base):
    __tablename__ = "foods"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)  # name of the food
    calories = Column(Numeric(10,2), nullable=False)  # kcal
    protein = Column(Numeric(10,2), nullable=True)  # grams
    carbs = Column(Numeric(10,2), nullable=True)  # grams
    fat = Column(Numeric(10,2), nullable=True)  # grams
    serving_unit = Column(String, nullable=True)  # serving unit of the food
    serving_size = Column(Numeric(10,2), nullable=True, default=1.0)  # serving size of the food
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    

    # Relationships
    logs = relationship("ConsumptionLog", back_populates="food")