from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True

class UserInDBBase(UserBase):
    id: int
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str

# Conversation Schemas
class ConversationBase(BaseModel):
    title: Optional[str] = None

class ConversationInDBBase(ConversationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Conversation(ConversationInDBBase):
    pass

# Message Schemas
class MessageBase(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class MessageInDBBase(MessageBase):
    id: int
    conversation_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Message(MessageInDBBase):
    pass

# Response Schemas
class ChatResponse(BaseModel):
    message: str
    conversation_id: int
    model_used: str
    tokens_used: Optional[int] = None

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None

# Health Schemas
class ActivityDailyBase(BaseModel):
    date: date
    steps: Optional[int] = Field(None, ge=0)
    move_kcal: Optional[float] = Field(None, ge=0)
    exercise_min: Optional[int] = Field(None, ge=0)
    stand_hours: Optional[int] = Field(None, ge=0, le=24)
    source: Optional[str] = None

class ActivityDailyInDBBase(ActivityDailyBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ActivityDailyInDBBase2(ActivityDailyBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ActivityDaily(ActivityDailyInDBBase):
    pass

class NutritionDailyBase(BaseModel):
    date: date
    calories: Optional[float] = Field(None, ge=0, le=12000)
    protein_g: Optional[float] = Field(None, ge=0, le=500)
    carbs_g: Optional[float] = Field(None, ge=0, le=1200)
    fats_g: Optional[float] = Field(None, ge=0, le=400)
    fiber_g: Optional[float] = Field(None, ge=0, le=200)
    source: Optional[str] = None
    sodium_mg: Optional[float] = None
    potassium_mg: Optional[float] = None
    cholesterol_mg: Optional[float] = None
    sat_fat_g: Optional[float] = None
    mono_fat_g: Optional[float] = None
    poly_fat_g: Optional[float] = None
    vitamin_c_mg: Optional[float] = None
    calcium_mg: Optional[float] = None
    iron_mg: Optional[float] = None

class NutritionDailyInDBBase(NutritionDailyBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class NutritionDaily(NutritionDailyInDBBase):
    pass

class SleepDailyBase(BaseModel):
    date: date
    time_asleep_min: Optional[int] = Field(None, ge=0, le=1200)
    efficiency: Optional[float] = None
    rem_min: Optional[int] = None
    deep_min: Optional[int] = None
    source: Optional[str] = None
    core_min: Optional[int] = None
    awake_min: Optional[int] = None
    in_bed_min: Optional[int] = None
    sleep_start_at: Optional[datetime] = None
    sleep_end_at: Optional[datetime] = None
    in_bed_start_at: Optional[datetime] = None
    in_bed_end_at: Optional[datetime] = None


class SleepDailyInDBBase(SleepDailyBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SleepDaily(SleepDailyInDBBase):
    pass

class WeightDailyBase(BaseModel):
    date: date
    weight_lb: float = Field(..., gt=0)
    source: Optional[str] = None
    lean_mass_lb: Optional[float] = None
    body_fat_pct: Optional[float] = None
    bmi: Optional[float] = None

class WeightDailyInDBBase(WeightDailyBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class WeightDaily(WeightDailyInDBBase):
    pass

class WorkoutSessionBase(BaseModel):
    session_date: date
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    notes: Optional[str] = None
    workout_type: Optional[str] = None
    duration_sec: Optional[float] = None
    distance_mi: Optional[float] = None
    energy_kcal: Optional[float] = None
    avg_hr: Optional[int] = None
    max_hr: Optional[int] = None
    external_id: Optional[str] = None
    source: Optional[str] = "apple_health"

class WorkoutSessionInDBBase(WorkoutSessionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class WorkoutSession(WorkoutSessionInDBBase):
    pass

class WorkoutSetBase(BaseModel):
    session_id: Optional[int] = None
    ts: Optional[datetime] = None
    lift: str
    set_number: Optional[int] = None
    reps: Optional[int] = Field(None, ge=1, le=50)
    load_lb: Optional[float] = Field(None, ge=0)
    rpe: Optional[float] = Field(None, ge=0, le=10)
    e1rm_lb: Optional[float] = None

class WorkoutSetInDBBase(WorkoutSetBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class WorkoutSet(WorkoutSetInDBBase):
    pass 