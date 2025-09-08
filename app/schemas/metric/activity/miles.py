from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# Activity Miles Schemas
class ActivityMilesCreate(BaseModel):
    date: datetime = Field(..., description="Date and time of activity")
    miles: Optional[float] = Field(None, ge=0, description="Miles traveled")
    distance_km: Optional[float] = Field(
        None, ge=0, description="Distance in kilometers"
    )
    pace_per_mile: Optional[float] = Field(
        None, ge=0, description="Pace per mile in minutes"
    )
    pace_per_km: Optional[float] = Field(
        None, ge=0, description="Pace per km in minutes"
    )
    activity_type: Optional[str] = Field(
        None, description="Activity type (e.g., walking, running, cycling)"
    )
    source: str = Field(..., description="Source of the data")


class ActivityMilesUpdate(BaseModel):
    date: Optional[datetime] = Field(None, description="Date and time of activity")
    miles: Optional[float] = Field(None, ge=0, description="Miles traveled")
    distance_km: Optional[float] = Field(
        None, ge=0, description="Distance in kilometers"
    )
    pace_per_mile: Optional[float] = Field(
        None, ge=0, description="Pace per mile in minutes"
    )
    pace_per_km: Optional[float] = Field(
        None, ge=0, description="Pace per km in minutes"
    )
    activity_type: Optional[str] = Field(None, description="Activity type")
    source: Optional[str] = Field(None, description="Source of the data")


class ActivityMilesResponse(BaseModel):
    id: str
    user_id: str
    date: datetime
    miles: Optional[float]
    distance_km: Optional[float]
    pace_per_mile: Optional[float]
    pace_per_km: Optional[float]
    activity_type: Optional[str]
    source: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Response schemas
class ActivityMilesCreateResponse(BaseModel):
    message: str
    miles: ActivityMilesResponse


class ActivityMilesUpdateResponse(BaseModel):
    message: str
    miles: ActivityMilesResponse


class ActivityMilesDeleteResponse(BaseModel):
    message: str
    deleted_count: int


class ActivityMilesExportResponse(BaseModel):
    records: list[ActivityMilesResponse]
    total_count: int
    user_id: str
