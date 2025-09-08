from typing import List, Optional

from pydantic import BaseModel, Field


# Active Calories Data Point Schema
class ActiveCaloriesDataPoint(BaseModel):
    calories_burned: Optional[float] = Field(
        None, ge=0, description="Calories burned in this hour"
    )
    date: str = Field(..., description="ISO datetime string")
    source: str = Field(
        ..., description="Source of the data (e.g., Apple Watch, Fitbit)"
    )


# Active Calories Metric Schema
class ActiveCaloriesMetric(BaseModel):
    name: str = Field(..., description="Metric name (e.g., active_calories)")
    data: List[ActiveCaloriesDataPoint] = Field(
        ..., description="List of active calories data points"
    )


# Active Calories Record Schema
class ActiveCaloriesRecord(BaseModel):
    data: ActiveCaloriesMetric = Field(..., description="Active calories metric data")


# Active Calories Ingest Request Schema
class ActiveCaloriesIngestRequest(BaseModel):
    record: ActiveCaloriesRecord = Field(..., description="Active calories record data")


# Active Calories Ingest Response Schema
class ActiveCaloriesIngestResponse(BaseModel):
    message: str
    records_processed: int
    metrics_processed: List[str]
    user_id: str
    source: str


# Active Calories Export Response Schema
class ActiveCaloriesRecord(BaseModel):
    id: str
    user_id: str
    date: str
    calories_burned: Optional[float]
    source: str
    created_at: Optional[str]
    updated_at: Optional[str]


class ActiveCaloriesExportResponse(BaseModel):
    records: List[ActiveCaloriesRecord]
    total_count: int
    user_id: str
