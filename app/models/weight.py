from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class Weight(Base):
    __tablename__ = "weight"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    weight = Column(Numeric, nullable=False)  # Weight measurement in kg or lbs
    body_fat_percentage = Column(
        Numeric, nullable=True
    )  # Body fat percentage if measured
    muscle_mass_percentage = Column(
        Numeric, nullable=True
    )  # Muscle mass percentage if measured
    notes = Column(String, nullable=True)  # Additional notes about the measurement
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")
