from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class FoodCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Name of the food")
    calories: float = Field(..., ge=0, description="Calories per serving in kcal")
    brand: Optional[str] = Field(None, description="Brand of the food")
    protein: Optional[float] = Field(
        None, ge=0, description="Protein per serving in grams"
    )
    carbs: Optional[float] = Field(
        None, ge=0, description="Carbohydrates per serving in grams"
    )
    fat: Optional[float] = Field(
        None, ge=0, description="Fat per serving in grams"
    )
    serving_unit: Optional[str] = Field(
        default="serving", description="Unit the serving size refers to (e.g., g, oz, slice)"
    )
    serving_size: Optional[float] = Field(
        default=1.0, ge=0, description="Base serving size quantity for the food"
    )


class FoodUpdate(BaseModel):
    name: Optional[str] = Field(
        None, min_length=1, description="Name of the food"
    )
    calories: Optional[float] = Field(
        None, ge=0, description="Calories per serving in kcal"
    )
    brand: Optional[str] = Field(None, description="Brand of the food")
    protein: Optional[float] = Field(
        None, ge=0, description="Protein per serving in grams"
    )
    carbs: Optional[float] = Field(
        None, ge=0, description="Carbohydrates per serving in grams"
    )
    fat: Optional[float] = Field(
        None, ge=0, description="Fat per serving in grams"
    )
    serving_unit: Optional[str] = Field(
        None, description="Unit the serving size refers to (e.g., g, oz, slice)"
    )
    serving_size: Optional[float] = Field(
        None, ge=0, description="Base serving size quantity for the food"
    )


class FoodResponse(BaseModel):
    id: str
    name: str
    calories: float
    brand: Optional[str]
    protein: Optional[float]
    carbs: Optional[float]
    fat: Optional[float]
    serving_unit: Optional[str]
    serving_size: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class FoodListResponse(BaseModel):
    records: List[FoodResponse]
    total_count: int


class FoodCreateResponse(BaseModel):
    message: str
    food: FoodResponse


class FoodDeleteResponse(BaseModel):
    message: str
    deleted_count: int
