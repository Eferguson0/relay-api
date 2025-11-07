from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ConsumptionLogCreate(BaseModel):
    logged_at: str = Field(
        ..., description="ISO datetime string of when the food was consumed"
    )    
    food_id: str = Field(..., description="ID of the food consumed")
    servings: float = Field(
        default=1.0, gt=0, description="Quantity of the serving units consumed"
    )
    serving_unit: Optional[str] = Field(
        default="serving", description="Unit the serving size refers to (e.g., g, oz, slice)"
    )
    calories_total: float = Field(
        ..., ge=0, description="Total calories consumed"
    )
    protein_total: Optional[float] = Field(
        None, ge=0, description="Total protein consumed"
    )
    carbs_total: Optional[float] = Field(
        None, ge=0, description="Total carbs consumed"
    )
    fat_total: Optional[float] = Field(
        None, ge=0, description="Total fat consumed"
    )
    is_saved: bool = Field(default=False, description="Whether the food is saved")


class ConsumptionLogUpdate(BaseModel):
    logged_at: Optional[str] = Field(
        None, description="ISO datetime string of when the food was consumed"
    )
    servings: Optional[float] = Field(
        None, gt=0, description="Quantity of the serving units consumed"
    )
    serving_unit: Optional[str] = Field(
        None, description="Unit the serving size refers to (e.g., g, oz, slice)"
    )
    calories_total: Optional[float] = Field(
        None, ge=0, description="Total calories consumed"
    )
    protein_total: Optional[float] = Field(
        None, ge=0, description="Total protein consumed"
    )
    carbs_total: Optional[float] = Field(
        None, ge=0, description="Total carbs consumed"
    )
    fat_total: Optional[float] = Field(
        None, ge=0, description="Total fat consumed"
    )
    is_saved: Optional[bool] = Field(None, description="Whether the food is saved")


class ConsumptionLogResponse(BaseModel):
    id: str
    user_id: str
    logged_at: datetime
    food_id: str
    servings: float
    serving_unit: Optional[str]
    calories_total: float
    protein_total: Optional[float]
    carbs_total: Optional[float]
    fat_total: Optional[float]
    is_saved: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ConsumptionLogListResponse(BaseModel):
    records: List[ConsumptionLogResponse]
    total_count: int


class ConsumptionLogCreateResponse(BaseModel):
    message: str
    log: ConsumptionLogResponse


class ConsumptionLogDeleteResponse(BaseModel):
    message: str
    deleted_count: int


class DailyConsumptionAggregation(BaseModel):
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    total_calories: float
    total_protein: Optional[float] = None
    total_carbs: Optional[float] = None
    total_fat: Optional[float] = None
    log_count: int = 0
    logs: List[ConsumptionLogResponse] = []