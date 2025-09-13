from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# Goal General Schemas
class GoalGeneralCreate(BaseModel):
    goal_description: str = Field(
        ..., min_length=1, description="Description of the general goal"
    )
    target_date: Optional[datetime] = Field(
        None, description="Optional target date for the goal"
    )
    # Weight-related goal fields
    target_weight: Optional[float] = Field(
        None, ge=0, description="Target weight in kg or lbs"
    )
    target_body_fat_percentage: Optional[float] = Field(
        None, ge=0, le=100, description="Target body fat percentage (0-100)"
    )
    target_muscle_mass_percentage: Optional[float] = Field(
        None, ge=0, le=100, description="Target muscle mass percentage (0-100)"
    )


class GoalGeneralUpdate(BaseModel):
    goal_description: Optional[str] = Field(
        None, min_length=1, description="Description of the general goal"
    )
    target_date: Optional[datetime] = Field(
        None, description="Optional target date for the goal"
    )
    # Weight-related goal fields
    target_weight: Optional[float] = Field(
        None, ge=0, description="Target weight in kg or lbs"
    )
    target_body_fat_percentage: Optional[float] = Field(
        None, ge=0, le=100, description="Target body fat percentage (0-100)"
    )
    target_muscle_mass_percentage: Optional[float] = Field(
        None, ge=0, le=100, description="Target muscle mass percentage (0-100)"
    )


class GoalGeneralResponse(BaseModel):
    id: str
    user_id: str
    goal_description: str
    target_date: Optional[datetime]
    # Weight-related goal fields
    target_weight: Optional[float]
    target_body_fat_percentage: Optional[float]
    target_muscle_mass_percentage: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Response schemas
class GoalGeneralCreateResponse(BaseModel):
    message: str
    goal: GoalGeneralResponse


class GoalGeneralUpdateResponse(BaseModel):
    message: str
    goal: GoalGeneralResponse


class GoalGeneralDeleteResponse(BaseModel):
    message: str
    deleted_count: int


# Bulk Operations Schemas
class GoalGeneralBulkCreate(BaseModel):
    records: List[GoalGeneralCreate] = Field(
        ..., description="List of general goal records to create/update"
    )


class GoalGeneralBulkCreateResponse(BaseModel):
    message: str
    created_count: int
    updated_count: int
    total_processed: int
    records: List[GoalGeneralResponse]
