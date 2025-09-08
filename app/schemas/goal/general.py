from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# Goal General Schemas
class GoalGeneralCreate(BaseModel):
    goal_description: str = Field(
        ..., min_length=1, description="Description of the general goal"
    )
    target_date: Optional[datetime] = Field(
        None, description="Optional target date for the goal"
    )


class GoalGeneralUpdate(BaseModel):
    goal_description: Optional[str] = Field(
        None, min_length=1, description="Description of the general goal"
    )
    target_date: Optional[datetime] = Field(
        None, description="Optional target date for the goal"
    )


class GoalGeneralResponse(BaseModel):
    id: str
    user_id: str
    goal_description: str
    target_date: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Response schemas
class GoalGeneralCreateResponse(BaseModel):
    message: str
    goal: GoalGeneralResponse


class GoalGeneralUpdateResponse(BaseModel):
    message: str
    goal: GoalGeneralResponse


class GoalGeneralDeleteResponse(BaseModel):
    message: str
    deleted_count: int
