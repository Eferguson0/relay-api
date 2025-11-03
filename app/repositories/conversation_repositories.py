from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.chat.conversation import ChatConversation

class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, conversation: ChatConversation) -> ChatConversation:
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get_all(self, user_id: str) -> List[ChatConversation]:
        return self.db.query(ChatConversation).filter(
            ChatConversation.user_id == user_id
        ).order_by(ChatConversation.created_at.desc()).all()