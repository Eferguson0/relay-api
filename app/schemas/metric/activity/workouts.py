from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from app.models.enums import DataSource


# Activity Workouts Schemas
class ActivityWorkoutsCreate(BaseModel):
    date: datetime = Field(..., description="Date and time of workout")
    workout_name: Optional[str] = Field(None, description="Name of the workout")
    workout_type: str = Field(
        ..., description="Type of workout (e.g., cardio, strength, flexibility)"
    )
    duration_minutes: Optional[int] = Field(
        None, ge=0, description="Duration in minutes"
    )
    calories_burned: Optional[float] = Field(
        None, ge=0, description="Calories burned during workout"
    )
    distance_miles: Optional[float] = Field(
        None, ge=0, description="Distance covered in miles"
    )
    avg_heart_rate: Optional[int] = Field(
        None, ge=0, le=300, description="Average heart rate during workout"
    )
    max_heart_rate: Optional[int] = Field(
        None, ge=0, le=300, description="Maximum heart rate during workout"
    )
    intensity: Optional[str] = Field(
        None, description="Intensity level: low, moderate, high"
    )
    source: Optional[DataSource] = Field(None, description="Source of the data")
    notes: Optional[str] = Field(None, description="Additional notes about the workout")


class ActivityWorkoutsResponse(BaseModel):
    id: str
    user_id: str
    date: datetime
    workout_name: Optional[str]
    workout_type: str
    duration_minutes: Optional[int]
    calories_burned: Optional[float]
    distance_miles: Optional[float]
    avg_heart_rate: Optional[int]
    max_heart_rate: Optional[int]
    intensity: Optional[str]
    source: Optional[DataSource]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Response schemas
class ActivityWorkoutsCreateResponse(BaseModel):
    message: str
    workout: ActivityWorkoutsResponse


class ActivityWorkoutsDeleteResponse(BaseModel):
    message: str
    deleted_count: int


class ActivityWorkoutsExportResponse(BaseModel):
    records: list[ActivityWorkoutsResponse]
    total_count: int
    user_id: str


# Bulk Operations Schemas
class ActivityWorkoutsBulkCreate(BaseModel):
    records: List[ActivityWorkoutsCreate] = Field(
        ..., description="List of workout records to create/update"
    )


class ActivityWorkoutsBulkCreateResponse(BaseModel):
    message: str
    created_count: int
    updated_count: int
    total_processed: int
    records: List[ActivityWorkoutsResponse]
