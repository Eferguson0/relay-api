from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class UserFoodPreferenceCreate(BaseModel):
    food_id: str = Field(..., description="ID of the food")
    is_saved: bool = Field(default=False, description="Whether the food is saved")
    serving_unit: Optional[str] = Field(
        None, description="Unit the serving size refers to (e.g., g, oz, slice)"
    )
    serving_size: Optional[float] = Field(
        None, ge=0, description="Base serving size quantity for the food"
    )
    notes: Optional[str] = Field(None, description="Additional user notes about the food")


class UserFoodPreferenceUpdate(BaseModel):
    is_saved: Optional[bool] = Field(
        None, description="Whether the food is saved"
    )
    serving_unit: Optional[str] = Field(
        None, description="Unit the serving size refers to (e.g., g, oz, slice)"
    )
    serving_size: Optional[float] = Field(
        None, ge=0, description="Base serving size quantity for the food"
    )
    notes: Optional[str] = Field(None, description="Additional user notes about the food")


class UserFoodPreferenceResponse(BaseModel):
    id: str
    user_id: str
    food_id: str
    is_saved: bool
    serving_unit: Optional[str]
    serving_size: Optional[float]
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserFoodPreferenceListResponse(BaseModel):
    records: List[UserFoodPreferenceResponse]
    total_count: int


class UserFoodPreferenceCreateResponse(BaseModel):
    message: str
    preference: UserFoodPreferenceResponse


class UserFoodPreferenceDeleteResponse(BaseModel):
    message: str
    deleted_count: int
