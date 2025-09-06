from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# Weight record creation schema
class WeightCreate(BaseModel):
    weight: float = Field(..., gt=0, description="Weight measurement in kg or lbs")
    body_fat_percentage: Optional[float] = Field(
        None, ge=0, le=100, description="Body fat percentage (0-100)"
    )
    muscle_mass_percentage: Optional[float] = Field(
        None, ge=0, le=100, description="Muscle mass percentage (0-100)"
    )
    notes: Optional[str] = Field(
        None, max_length=500, description="Optional notes about the measurement"
    )


# Weight record update schema
class WeightUpdate(BaseModel):
    weight: Optional[float] = Field(
        None, gt=0, description="Weight measurement in kg or lbs"
    )
    body_fat_percentage: Optional[float] = Field(
        None, ge=0, le=100, description="Body fat percentage (0-100)"
    )
    muscle_mass_percentage: Optional[float] = Field(
        None, ge=0, le=100, description="Muscle mass percentage (0-100)"
    )


# Weight record response schema
class WeightResponse(BaseModel):
    id: int
    user_email: str
    weight: float
    body_fat_percentage: Optional[float]
    muscle_mass_percentage: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Weight record creation response schema
class WeightCreateResponse(BaseModel):
    message: str
    weight: WeightResponse


# Weight record update response schema
class WeightUpdateResponse(BaseModel):
    message: str
    weight: WeightResponse


# Weight record delete response schema
class WeightDeleteResponse(BaseModel):
    message: str
    deleted_count: int


# Weight export response schema (for getting all records)
class WeightExportResponse(BaseModel):
    records: list[WeightResponse]
    total_count: int
    user_email: str
