from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# Goal Weight Schemas
class GoalWeightCreate(BaseModel):
    date_hour: datetime = Field(..., description="Hour for the goal targets")
    weight: Optional[float] = Field(
        None, ge=0, description="Target weight in kg or lbs"
    )
    body_fat_percentage: Optional[float] = Field(
        None, ge=0, le=100, description="Target body fat percentage (0-100)"
    )
    muscle_mass_percentage: Optional[float] = Field(
        None, ge=0, le=100, description="Target muscle mass percentage (0-100)"
    )


class GoalWeightUpdate(BaseModel):
    weight: Optional[float] = Field(
        None, ge=0, description="Target weight in kg or lbs"
    )
    body_fat_percentage: Optional[float] = Field(
        None, ge=0, le=100, description="Target body fat percentage (0-100)"
    )
    muscle_mass_percentage: Optional[float] = Field(
        None, ge=0, le=100, description="Target muscle mass percentage (0-100)"
    )


class GoalWeightResponse(BaseModel):
    id: str
    user_id: str
    date_hour: datetime
    weight: Optional[float]
    body_fat_percentage: Optional[float]
    muscle_mass_percentage: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Response schemas
class GoalWeightCreateResponse(BaseModel):
    message: str
    goal: GoalWeightResponse


class GoalWeightUpdateResponse(BaseModel):
    message: str
    goal: GoalWeightResponse


class GoalWeightDeleteResponse(BaseModel):
    message: str
    deleted_count: int
