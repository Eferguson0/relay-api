from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ConsumptionLogCreate(BaseModel):
    food_id: str = Field(..., description="ID of the food consumed")
    datetime: str = Field(
        ..., description="ISO datetime string of when the food was consumed"
    )
    quantity: float = Field(
        ..., ge=0, description="Quantity of the food consumed"
    )


class ConsumptionLogResponse(BaseModel):
    id: str
    user_id: str
    datetime: datetime
    food_id: str
    quantity: float
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

