from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


# Active Calories Schemas
class ActiveCaloriesDataPoint(BaseModel):
    calories_burned: Optional[float] = Field(None, ge=0, le=2000)
    date: str
    source: str

    @field_validator("calories_burned", mode="before")
    @classmethod
    def round_down_float(cls, v):
        if v is not None and isinstance(v, (int, float)):
            return float(v)
        return v


class ActiveCaloriesMetric(BaseModel):
    name: str
    data: List[ActiveCaloriesDataPoint]
    units: str


class ActiveCaloriesRecordData(BaseModel):
    metrics: List[ActiveCaloriesMetric]


class ActiveCaloriesRecord(BaseModel):
    data: ActiveCaloriesRecordData


class ActiveCaloriesMetadata(BaseModel):
    id: str
    private: bool
    createdAt: str
    name: str


class ActiveCaloriesIngestRequest(BaseModel):
    record: ActiveCaloriesRecord
    metadata: ActiveCaloriesMetadata


class ActiveCaloriesIngestResponse(BaseModel):
    message: str
    records_processed: int
    metrics_processed: List[str]
    user_id: str
    source: str


# Hourly Steps Schemas
class HourlyStepsDataPoint(BaseModel):
    steps: Optional[int] = Field(None, ge=0, le=10000)
    date: str
    source: str

    @field_validator("steps", mode="before")
    @classmethod
    def round_down_float(cls, v):
        if v is not None and isinstance(v, (int, float)):
            return int(v)
        return v


class HourlyStepsMetric(BaseModel):
    name: str
    data: List[HourlyStepsDataPoint]
    units: str


class HourlyStepsRecordData(BaseModel):
    metrics: List[HourlyStepsMetric]


class HourlyStepsRecord(BaseModel):
    data: HourlyStepsRecordData


class HourlyStepsMetadata(BaseModel):
    id: str
    private: bool
    createdAt: str
    name: str


class HourlyStepsIngestRequest(BaseModel):
    record: HourlyStepsRecord
    metadata: HourlyStepsMetadata


class HourlyStepsIngestResponse(BaseModel):
    message: str
    records_processed: int
    metrics_processed: List[str]
    user_id: str
    source: str


# Export Schemas
class ActiveCaloriesExportResponse(BaseModel):
    records: List[dict]
    total_count: int
    user_id: str


class HourlyStepsExportResponse(BaseModel):
    records: List[dict]
    total_count: int
    user_id: str
