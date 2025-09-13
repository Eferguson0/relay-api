from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# Goal Macros Schemas
class GoalMacrosCreate(BaseModel):
    calories: Optional[float] = Field(None, ge=0, description="Target calories")
    protein: Optional[float] = Field(None, ge=0, description="Target protein in grams")
    carbs: Optional[float] = Field(None, ge=0, description="Target carbs in grams")
    fat: Optional[float] = Field(None, ge=0, description="Target fat in grams")
    calorie_deficit: Optional[float] = Field(
        None, ge=0, description="Calorie deficit target"
    )


class GoalMacrosUpdate(BaseModel):
    calories: Optional[float] = Field(None, ge=0, description="Target calories")
    protein: Optional[float] = Field(None, ge=0, description="Target protein in grams")
    carbs: Optional[float] = Field(None, ge=0, description="Target carbs in grams")
    fat: Optional[float] = Field(None, ge=0, description="Target fat in grams")
    calorie_deficit: Optional[float] = Field(
        None, ge=0, description="Calorie deficit target"
    )


class GoalMacrosResponse(BaseModel):
    id: str
    user_id: str
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


# Bulk Operations Schemas
class GoalMacrosBulkCreate(BaseModel):
    records: List[GoalMacrosCreate] = Field(
        ..., description="List of macro goal records to create/update"
    )


class GoalMacrosBulkCreateResponse(BaseModel):
    message: str
    created_count: int
    updated_count: int
    total_processed: int
    records: List[GoalMacrosResponse]
