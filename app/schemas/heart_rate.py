from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


# Heart Rate Ingest Request Schemas
class MetricDataPoint(BaseModel):
    Max: Optional[int] = Field(None, ge=0, le=300)
    date: str
    Min: Optional[int] = Field(None, ge=0, le=300)
    Avg: Optional[float] = Field(None, ge=0, le=300)
    source: str

    @field_validator("Min", "Max", mode="before")
    @classmethod
    def round_down_float(cls, v):
        if v is not None and isinstance(v, (int, float)):
            return int(v)
        return v


class Metric(BaseModel):
    name: str
    data: List[MetricDataPoint]
    units: str


class RecordData(BaseModel):
    metrics: List[Metric]


class Record(BaseModel):
    data: RecordData


class Metadata(BaseModel):
    id: str
    private: bool
    createdAt: str
    name: str


class HeartRateIngestRequest(BaseModel):
    record: Record
    metadata: Metadata


# Heart Rate Ingest Response Schema
class HeartRateIngestResponse(BaseModel):
    message: str
    records_processed: int
    metrics_processed: List[str]
    user_id: str
    source: str
