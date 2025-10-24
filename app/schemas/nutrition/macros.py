from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

"""
# Macros Ingest Request Schemas
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


class NutritionMacrosIngestRequest(BaseModel):
    data: List[MacroDataPoint]


# Macros Ingest Response Schema
class NutritionMacrosIngestResponse(BaseModel):
    message: str
    records_processed: int
    user_id: str
    total_calories: Optional[float] = None
    total_protein: Optional[float] = None
    total_carbs: Optional[float] = None
    total_fat: Optional[float] = None
"""

# Macros Export Response Schema
class NutritionMacrosRecord(BaseModel):
    id: str
    user_id: str
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


class NutritionMacrosExportResponse(BaseModel):
    records: List[NutritionMacrosRecord]
    total_count: int
    total_calories: Optional[float] = None
    total_protein: Optional[float] = None
    total_carbs: Optional[float] = None
    total_fat: Optional[float] = None


# Single Macros Record Schemas
class NutritionMacrosRecordCreate(BaseModel):
    datetime: str = Field(
        ..., description="ISO datetime string of when the meal was consumed"
    )
    protein: Optional[float] = Field(None, ge=0, description="Protein in grams")
    carbs: Optional[float] = Field(None, ge=0, description="Carbs in grams")
    fat: Optional[float] = Field(None, ge=0, description="Fat in grams")
    calories: Optional[float] = Field(None, ge=0, description="Calories in kcal")
    meal_name: Optional[str] = Field(None, description="Name of the meal")
    notes: Optional[str] = Field(None, description="Additional notes about the meal")

"""
class NutritionMacrosRecordResponse(BaseModel):
    id: str
    user_id: str
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
"""

# Bulk Operations Schemas
class NutritionMacrosBulkCreate(BaseModel):
    records: List[NutritionMacrosRecordCreate] = Field(
        ..., description="List of nutrition macro records to create/update"
    )


class NutritionMacrosBulkCreateResponse(BaseModel):
    message: str
    created_count: int
    updated_count: int
    total_processed: int
    records: List[NutritionMacrosRecord]


# Daily Aggregation Schema
class DailyAggregation(BaseModel):
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    total_calories: Optional[float] = None
    total_protein: Optional[float] = None
    total_carbs: Optional[float] = None
    total_fat: Optional[float] = None
    meal_count: int = 0
    meals: List[NutritionMacrosRecord] = []


class DailyAggregationResponse(BaseModel):
    date: str
    aggregations: List[DailyAggregation]
    total_days: int


# Delete Response Schema
class NutritionMacrosDeleteResponse(BaseModel):
    message: str
    deleted_count: int
