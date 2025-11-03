from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class ConsumptionLog(Base):
    __tablename__ = "consumption_logs"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("auth_users.id"), nullable=False, index=True)
    datetime = Column(DateTime(timezone=True), nullable=False, index=True)
    food_id = Column(String, ForeignKey("foods.id"), nullable=False)
    quantity = Column(Numeric(10,2), nullable=False, default=1.0)  # quantity of the food
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("AuthUser")
    food = relationship("Food", back_populates="logs")