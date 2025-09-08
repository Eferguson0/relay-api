from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# Sleep Daily Schemas
class SleepDailyCreate(BaseModel):
    sleep_date: datetime = Field(..., description="Date of sleep (start of sleep day)")
    bedtime: Optional[datetime] = Field(None, description="When user went to bed")
    wake_time: Optional[datetime] = Field(None, description="When user woke up")
    total_sleep_minutes: Optional[int] = Field(
        None, ge=0, description="Total sleep duration in minutes"
    )
    deep_sleep_minutes: Optional[int] = Field(
        None, ge=0, description="Deep sleep duration in minutes"
    )
    light_sleep_minutes: Optional[int] = Field(
        None, ge=0, description="Light sleep duration in minutes"
    )
    rem_sleep_minutes: Optional[int] = Field(
        None, ge=0, description="REM sleep duration in minutes"
    )
    awake_minutes: Optional[int] = Field(
        None, ge=0, description="Time awake during sleep period"
    )
    sleep_efficiency: Optional[float] = Field(
        None, ge=0, le=100, description="Sleep efficiency percentage"
    )
    sleep_quality_score: Optional[int] = Field(
        None, ge=1, le=10, description="Sleep quality score (1-10)"
    )
    source: str = Field(..., description="Source of the data")
    notes: Optional[str] = Field(None, description="Additional notes about sleep")


class SleepDailyUpdate(BaseModel):
    sleep_date: Optional[datetime] = Field(None, description="Date of sleep")
    bedtime: Optional[datetime] = Field(None, description="When user went to bed")
    wake_time: Optional[datetime] = Field(None, description="When user woke up")
    total_sleep_minutes: Optional[int] = Field(
        None, ge=0, description="Total sleep duration in minutes"
    )
    deep_sleep_minutes: Optional[int] = Field(
        None, ge=0, description="Deep sleep duration in minutes"
    )
    light_sleep_minutes: Optional[int] = Field(
        None, ge=0, description="Light sleep duration in minutes"
    )
    rem_sleep_minutes: Optional[int] = Field(
        None, ge=0, description="REM sleep duration in minutes"
    )
    awake_minutes: Optional[int] = Field(
        None, ge=0, description="Time awake during sleep period"
    )
    sleep_efficiency: Optional[float] = Field(
        None, ge=0, le=100, description="Sleep efficiency percentage"
    )
    sleep_quality_score: Optional[int] = Field(
        None, ge=1, le=10, description="Sleep quality score (1-10)"
    )
    source: Optional[str] = Field(None, description="Source of the data")
    notes: Optional[str] = Field(None, description="Additional notes about sleep")


class SleepDailyResponse(BaseModel):
    id: str
    user_id: str
    sleep_date: datetime
    bedtime: Optional[datetime]
    wake_time: Optional[datetime]
    total_sleep_minutes: Optional[int]
    deep_sleep_minutes: Optional[int]
    light_sleep_minutes: Optional[int]
    rem_sleep_minutes: Optional[int]
    awake_minutes: Optional[int]
    sleep_efficiency: Optional[float]
    sleep_quality_score: Optional[int]
    source: str
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Response schemas
class SleepDailyCreateResponse(BaseModel):
    message: str
    sleep: SleepDailyResponse


class SleepDailyUpdateResponse(BaseModel):
    message: str
    sleep: SleepDailyResponse


class SleepDailyDeleteResponse(BaseModel):
    message: str
    deleted_count: int


class SleepDailyExportResponse(BaseModel):
    records: list[SleepDailyResponse]
    total_count: int
    user_id: str
