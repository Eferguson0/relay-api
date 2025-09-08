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


class BodyComposition(Base):
    __tablename__ = "body_composition"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("auth_users.id"), nullable=False)
    measurement_date = Column(DateTime(timezone=True), nullable=False)
    weight = Column(Numeric, nullable=True)  # Weight in kg or lbs
    body_fat_percentage = Column(Numeric, nullable=True)  # Body fat percentage
    muscle_mass_percentage = Column(Numeric, nullable=True)  # Muscle mass percentage
    bone_density = Column(Numeric, nullable=True)  # Bone density
    water_percentage = Column(Numeric, nullable=True)  # Water percentage
    visceral_fat = Column(Numeric, nullable=True)  # Visceral fat level
    bmr = Column(Numeric, nullable=True)  # Basal Metabolic Rate
    measurement_method = Column(String, nullable=True)  # e.g., "DEXA", "BIA", "Scale"
    notes = Column(String, nullable=True)  # Additional notes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Unique constraint to prevent duplicate measurements on same date
    __table_args__ = (UniqueConstraint("user_id", "measurement_date"),)

    # Relationships
    user = relationship("AuthUser")
