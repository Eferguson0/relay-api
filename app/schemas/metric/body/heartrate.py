from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.enums import DataSource


# Heart Rate Export Response Schema
class HeartRateExportRecord(BaseModel):
    id: str
    user_id: str
    date_hour: datetime
    heart_rate: Optional[int]
    min_hr: Optional[int]
    avg_hr: Optional[float]
    max_hr: Optional[int]
    resting_hr: Optional[int]
    heart_rate_variability: Optional[float]
    source: DataSource
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class HeartRateExportResponse(BaseModel):
    records: List[HeartRateExportRecord]
    total_count: int
    user_id: str


# CRUD Schemas
class HeartRateCreate(BaseModel):
    date_hour: datetime = Field(
        ..., description="Date and hour for the heart rate record"
    )
    heart_rate: Optional[int] = Field(
        None, ge=0, le=300, description="Heart rate in BPM"
    )
    min_hr: Optional[int] = Field(None, ge=0, le=300, description="Minimum heart rate")
    avg_hr: Optional[float] = Field(
        None, ge=0, le=300, description="Average heart rate"
    )
    max_hr: Optional[int] = Field(None, ge=0, le=300, description="Maximum heart rate")
    resting_hr: Optional[int] = Field(
        None, ge=0, le=300, description="Resting heart rate"
    )
    heart_rate_variability: Optional[float] = Field(
        None, ge=0, description="Heart rate variability"
    )
    source: DataSource = Field(..., description="Source of the data")


class HeartRateResponse(BaseModel):
    id: str
    user_id: str
    date_hour: datetime
    heart_rate: Optional[int]
    min_hr: Optional[int]
    avg_hr: Optional[float]
    max_hr: Optional[int]
    resting_hr: Optional[int]
    heart_rate_variability: Optional[float]
    source: DataSource
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class HeartRateCreateResponse(BaseModel):
    message: str
    heart_rate: HeartRateResponse


class HeartRateDeleteResponse(BaseModel):
    message: str
    deleted_count: int


# Bulk Operations Schemas
class HeartRateBulkCreate(BaseModel):
    records: List[HeartRateCreate] = Field(
        ..., description="List of heart rate records to create/update"
    )


class HeartRateBulkCreateResponse(BaseModel):
    message: str
    created_count: int
    updated_count: int
    total_processed: int
    records: List[HeartRateResponse]
