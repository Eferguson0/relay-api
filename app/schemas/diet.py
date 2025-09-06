from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# Diet Ingest Request Schemas
class MacroDataPoint(BaseModel):
    protein: Optional[float] = Field(None, ge=0, description="Protein in grams")
    carbs: Optional[float] = Field(None, ge=0, description="Carbs in grams")
    fat: Optional[float] = Field(None, ge=0, description="Fat in grams")
    calories: Optional[float] = Field(None, ge=0, description="Calories in kcal")
    meal_name: Optional[str] = Field(
        None, description="Name of the meal (e.g., Breakfast, Lunch, Dinner, Snack)"
    )
    notes: Optional[str] = Field(None, description="Additional notes about the meal")
    datetime: str = Field(
        ..., description="ISO datetime string of when the meal was consumed"
    )


class DietIngestRequest(BaseModel):
    data: List[MacroDataPoint]


# Diet Ingest Response Schema
class DietIngestResponse(BaseModel):
    message: str
    records_processed: int
    user_email: str
    total_calories: Optional[float] = None
    total_protein: Optional[float] = None
    total_carbs: Optional[float] = None
    total_fat: Optional[float] = None


# Diet Export Response Schema
class DietRecord(BaseModel):
    id: str
    user_email: str
    datetime: datetime
    protein: Optional[float]
    carbs: Optional[float]
    fat: Optional[float]
    calories: Optional[float]
    meal_name: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class DietExportResponse(BaseModel):
    records: List[DietRecord]
    total_count: int
    total_calories: Optional[float] = None
    total_protein: Optional[float] = None
    total_carbs: Optional[float] = None
    total_fat: Optional[float] = None


# Single Diet Record Schemas
class DietRecordCreate(BaseModel):
    datetime: str = Field(
        ..., description="ISO datetime string of when the meal was consumed"
    )
    protein: Optional[float] = Field(None, ge=0, description="Protein in grams")
    carbs: Optional[float] = Field(None, ge=0, description="Carbs in grams")
    fat: Optional[float] = Field(None, ge=0, description="Fat in grams")
    calories: Optional[float] = Field(None, ge=0, description="Calories in kcal")
    meal_name: Optional[str] = Field(None, description="Name of the meal")
    notes: Optional[str] = Field(None, description="Additional notes about the meal")


class DietRecordResponse(BaseModel):
    id: str
    user_email: str
    datetime: datetime
    protein: Optional[float]
    carbs: Optional[float]
    fat: Optional[float]
    calories: Optional[float]
    meal_name: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Daily Aggregation Schema
class DailyAggregation(BaseModel):
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    total_calories: Optional[float] = None
    total_protein: Optional[float] = None
    total_carbs: Optional[float] = None
    total_fat: Optional[float] = None
    meal_count: int = 0
    meals: List[DietRecord] = []


class DailyAggregationResponse(BaseModel):
    date: str
    aggregations: List[DailyAggregation]
    total_days: int


# Delete Response Schema
class DietDeleteResponse(BaseModel):
    message: str
    deleted_count: int
