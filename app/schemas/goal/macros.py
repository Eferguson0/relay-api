from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# Goal Macros Schemas
class GoalMacrosCreate(BaseModel):
    date_hour: datetime = Field(..., description="Hour for the goal targets")
    calories: Optional[float] = Field(None, ge=0, description="Target hourly calories")
    protein: Optional[float] = Field(
        None, ge=0, description="Target hourly protein in grams"
    )
    carbs: Optional[float] = Field(
        None, ge=0, description="Target hourly carbs in grams"
    )
    fat: Optional[float] = Field(None, ge=0, description="Target hourly fat in grams")
    calorie_deficit: Optional[float] = Field(
        None, ge=0, description="Calorie deficit target for this hour"
    )


class GoalMacrosUpdate(BaseModel):
    calories: Optional[float] = Field(None, ge=0, description="Target hourly calories")
    protein: Optional[float] = Field(
        None, ge=0, description="Target hourly protein in grams"
    )
    carbs: Optional[float] = Field(
        None, ge=0, description="Target hourly carbs in grams"
    )
    fat: Optional[float] = Field(None, ge=0, description="Target hourly fat in grams")
    calorie_deficit: Optional[float] = Field(
        None, ge=0, description="Calorie deficit target for this hour"
    )


class GoalMacrosResponse(BaseModel):
    id: str
    user_id: str
    date_hour: datetime
    calories: Optional[float]
    protein: Optional[float]
    carbs: Optional[float]
    fat: Optional[float]
    calorie_deficit: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Response schemas
class GoalMacrosCreateResponse(BaseModel):
    message: str
    goal: GoalMacrosResponse


class GoalMacrosUpdateResponse(BaseModel):
    message: str
    goal: GoalMacrosResponse


class GoalMacrosDeleteResponse(BaseModel):
    message: str
    deleted_count: int
