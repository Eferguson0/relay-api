from pydantic import BaseModel
from datetime import datetime

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

class ConversationCreate(BaseModel):
    title: str
    user_id: str

class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    status: str

class MessageCreate(BaseModel):
    content: str
    role: str
    user_id: str
    conversation_id: str

class MessageResponse(BaseModel):
    id: str
    content: str
    role: str
    created_at: datetime
    updated_at: datetime