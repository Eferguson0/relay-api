from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.chat.message import ChatMessage

class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, message: ChatMessage) -> ChatMessage:
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message