from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

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

class ConversationCreate(ConversationBase):
    pass

class ConversationUpdate(ConversationBase):
    pass

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

class MessageCreate(MessageBase):
    conversation_id: int

class MessageUpdate(MessageBase):
    pass

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