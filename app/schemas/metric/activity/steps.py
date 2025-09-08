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


# Steps Record Schema
class StepsRecord(BaseModel):
    data: StepsMetric = Field(..., description="Steps metric data")


# Steps Ingest Request Schema
class HourlyStepsIngestRequest(BaseModel):
    record: StepsRecord = Field(..., description="Steps record data")


# Steps Ingest Response Schema
class HourlyStepsIngestResponse(BaseModel):
    message: str
    records_processed: int
    metrics_processed: List[str]
    user_id: str
    source: str


# Steps Export Response Schema
class StepsRecord(BaseModel):
    id: str
    user_id: str
    date: str
    steps: Optional[int]
    source: str
    created_at: Optional[str]
    updated_at: Optional[str]


class HourlyStepsExportResponse(BaseModel):
    records: List[StepsRecord]
    total_count: int
    user_id: str
