from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# Activity Miles Schemas
class ActivityMilesCreate(BaseModel):
    date_hour: datetime = Field(..., description="Date and hour of activity")
    miles: Optional[float] = Field(None, ge=0, description="Miles traveled")
    activity_type: Optional[str] = Field(
        None, description="Activity type (e.g., walking, running, cycling)"
    )
    source: str = Field(..., description="Source of the data")


class ActivityMilesResponse(BaseModel):
    id: str
    user_id: str
    date_hour: datetime
    miles: Optional[float]
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


class ActivityMilesDeleteResponse(BaseModel):
    message: str
    deleted_count: int


class ActivityMilesExportResponse(BaseModel):
    records: list[ActivityMilesResponse]
    total_count: int
    user_id: str


# Bulk Operations Schemas
class ActivityMilesBulkCreate(BaseModel):
    records: List[ActivityMilesCreate] = Field(
        ..., description="List of activity miles records to create/update"
    )


class ActivityMilesBulkCreateResponse(BaseModel):
    message: str
    created_count: int
    updated_count: int
    total_processed: int
    records: List[ActivityMilesResponse]
