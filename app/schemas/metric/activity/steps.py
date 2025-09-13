from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# Steps Data Point Schema
class StepsDataPoint(BaseModel):
    steps: Optional[int] = Field(None, ge=0, description="Steps taken in this hour")
    date: str = Field(..., description="ISO datetime string")
    source: str = Field(
        ..., description="Source of the data (e.g., Apple Watch, Fitbit)"
    )


# Steps Metric Schema
class StepsMetric(BaseModel):
    name: str = Field(..., description="Metric name (e.g., hourly_steps)")
    data: List[StepsDataPoint] = Field(..., description="List of steps data points")


# Activity Steps Schemas
class ActivityStepsCreate(BaseModel):
    date_hour: datetime = Field(..., description="Date and hour for the steps record")
    steps: Optional[int] = Field(None, ge=0, description="Number of steps")
    source: str = Field(..., description="Source of the data")


class ActivityStepsResponse(BaseModel):
    id: str
    user_id: str
    date_hour: datetime
    steps: Optional[int]
    source: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Response schemas
class ActivityStepsCreateResponse(BaseModel):
    message: str
    record: ActivityStepsResponse


class ActivityStepsDeleteResponse(BaseModel):
    message: str
    deleted_count: int


class ActivityStepsExportResponse(BaseModel):
    records: List[ActivityStepsResponse]
    total_count: int
    user_id: str


# Ingest schemas
class ActivityStepsIngestRequest(BaseModel):
    record: ActivityStepsCreate = Field(..., description="Steps record data")


class ActivityStepsIngestResponse(BaseModel):
    message: str
    records_processed: int
    user_id: str


# Bulk Operations Schemas
class ActivityStepsBulkCreate(BaseModel):
    records: List[ActivityStepsCreate] = Field(
        ..., description="List of steps records to create/update"
    )


class ActivityStepsBulkCreateResponse(BaseModel):
    message: str
    created_count: int
    updated_count: int
    total_processed: int
    records: List[ActivityStepsResponse]
