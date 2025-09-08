from typing import List, Optional

from pydantic import BaseModel, Field


# Heart Rate Data Point Schema
class HeartRateDataPoint(BaseModel):
    heart_rate: Optional[int] = Field(
        None, ge=0, le=300, description="Heart rate in BPM"
    )
    date: str = Field(..., description="ISO datetime string")
    source: str = Field(
        ..., description="Source of the data (e.g., Apple Watch, Fitbit)"
    )


# Heart Rate Metric Schema
class HeartRateMetric(BaseModel):
    name: str = Field(..., description="Metric name (e.g., heart_rate)")
    data: List[HeartRateDataPoint] = Field(
        ..., description="List of heart rate data points"
    )


# Heart Rate Record Schema
class HeartRateRecord(BaseModel):
    data: HeartRateMetric = Field(..., description="Heart rate metric data")


# Heart Rate Ingest Request Schema
class HeartRateIngestRequest(BaseModel):
    record: HeartRateRecord = Field(..., description="Heart rate record data")


# Heart Rate Ingest Response Schema
class HeartRateIngestResponse(BaseModel):
    message: str
    records_processed: int
    metrics_processed: List[str]
    user_id: str
    source: str


# Heart Rate Export Response Schema
class HeartRateRecord(BaseModel):
    id: str
    user_id: str
    date: str
    heart_rate: Optional[int]
    min_hr: Optional[int]
    avg_hr: Optional[float]
    max_hr: Optional[int]
    resting_hr: Optional[int]
    heart_rate_variability: Optional[float]
    source: str
    created_at: Optional[str]
    updated_at: Optional[str]


class HeartRateExportResponse(BaseModel):
    records: List[HeartRateRecord]
    total_count: int
    user_id: str
