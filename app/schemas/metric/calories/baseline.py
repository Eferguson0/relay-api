from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, AliasChoices

from app.models.enums import DataSource


# Calories Baseline Schemas
class CaloriesBaselineCreate(BaseModel):
    date_hour: datetime = Field(
        ...,
        description="Date and time of measurement",
        serialization_alias="date",
        validation_alias=AliasChoices("date", "date_hour"),
    )
    baseline_calories: Optional[float] = Field(
        None, ge=0, description="Baseline calories burned"
    )
    bmr: Optional[float] = Field(None, ge=0, description="Basal Metabolic Rate")
    tdee: Optional[float] = Field(
        None, ge=0, description="Total Daily Energy Expenditure"
    )
    activity_level: Optional[str] = Field(
        None,
        description="Activity level: sedentary, lightly_active, moderately_active, very_active, extremely_active",
    )
    source: DataSource = Field(..., description="Source of the data")


class CaloriesBaselineResponse(BaseModel):
    id: str
    user_id: str
    date_hour: datetime = Field(
        ...,
        serialization_alias="date",
        validation_alias=AliasChoices("date", "date_hour"),
    )
    baseline_calories: Optional[float]
    bmr: Optional[float]
    source: DataSource
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
        populate_by_name = True


# Response schemas
class CaloriesBaselineCreateResponse(BaseModel):
    message: str
    baseline: CaloriesBaselineResponse


class CaloriesBaselineDeleteResponse(BaseModel):
    message: str
    deleted_count: int


class CaloriesBaselineExportResponse(BaseModel):
    records: list[CaloriesBaselineResponse]
    total_count: int
    user_id: str


# Bulk Operations Schemas
class CaloriesBaselineBulkCreate(BaseModel):
    records: List[CaloriesBaselineCreate] = Field(
        ..., description="List of baseline calories records to create/update"
    )


class CaloriesBaselineBulkCreateResponse(BaseModel):
    message: str
    created_count: int
    updated_count: int
    total_processed: int
    records: List[CaloriesBaselineResponse]
