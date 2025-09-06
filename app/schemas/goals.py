from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# Goal Weight Schemas
class GoalWeightCreate(BaseModel):
    weight: Optional[float] = Field(
        None, ge=0, description="Target weight in kg or lbs"
    )
    body_fat_percentage: Optional[float] = Field(
        None, ge=0, le=100, description="Target body fat percentage (0-100)"
    )
    muscle_mass_percentage: Optional[float] = Field(
        None, ge=0, le=100, description="Target muscle mass percentage (0-100)"
    )


class GoalWeightUpdate(BaseModel):
    weight: Optional[float] = Field(
        None, ge=0, description="Target weight in kg or lbs"
    )
    body_fat_percentage: Optional[float] = Field(
        None, ge=0, le=100, description="Target body fat percentage (0-100)"
    )
    muscle_mass_percentage: Optional[float] = Field(
        None, ge=0, le=100, description="Target muscle mass percentage (0-100)"
    )


class GoalWeightResponse(BaseModel):
    user_id: str
    weight: Optional[float]
    body_fat_percentage: Optional[float]
    muscle_mass_percentage: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Response schemas
class GoalWeightCreateResponse(BaseModel):
    message: str
    goal: GoalWeightResponse


class GoalWeightUpdateResponse(BaseModel):
    message: str
    goal: GoalWeightResponse


class GoalWeightDeleteResponse(BaseModel):
    message: str
    deleted_count: int


# Goal Daily Diet Schemas
class GoalDailyDietCreate(BaseModel):
    calories: Optional[float] = Field(None, ge=0, description="Target daily calories")
    protein: Optional[float] = Field(
        None, ge=0, description="Target daily protein in grams"
    )
    carbs: Optional[float] = Field(
        None, ge=0, description="Target daily carbs in grams"
    )
    fat: Optional[float] = Field(None, ge=0, description="Target daily fat in grams")


class GoalDailyDietUpdate(BaseModel):
    calories: Optional[float] = Field(None, ge=0, description="Target daily calories")
    protein: Optional[float] = Field(
        None, ge=0, description="Target daily protein in grams"
    )
    carbs: Optional[float] = Field(
        None, ge=0, description="Target daily carbs in grams"
    )
    fat: Optional[float] = Field(None, ge=0, description="Target daily fat in grams")


class GoalDailyDietResponse(BaseModel):
    user_id: str
    calories: Optional[float]
    protein: Optional[float]
    carbs: Optional[float]
    fat: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Response schemas for daily diet goals
class GoalDailyDietCreateResponse(BaseModel):
    message: str
    goal: GoalDailyDietResponse


class GoalDailyDietUpdateResponse(BaseModel):
    message: str
    goal: GoalDailyDietResponse


class GoalDailyDietDeleteResponse(BaseModel):
    message: str
    deleted_count: int


# Goal Message Schemas
class GoalMessageCreate(BaseModel):
    goal_message: str = Field(..., min_length=1, description="Goal message/description")


class GoalMessageUpdate(BaseModel):
    goal_message: str = Field(..., min_length=1, description="Goal message/description")


class GoalMessageResponse(BaseModel):
    user_id: str
    goal_message: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Response schemas for goal messages
class GoalMessageCreateResponse(BaseModel):
    message: str
    goal: GoalMessageResponse


class GoalMessageUpdateResponse(BaseModel):
    message: str
    goal: GoalMessageResponse


class GoalMessageDeleteResponse(BaseModel):
    message: str
    deleted_count: int
