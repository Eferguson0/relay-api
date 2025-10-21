from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.models.chat.conversation import ChatConversation
from app.models.chat.message import ChatMessage
from app.schemas.chat.assistant import ConversationCreate, ConversationResponse, MessageCreate, MessageResponse
from app.repositories.conversation_repositories import ConversationRepository
from app.repositories.message_repositories import MessageRepository

class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.conversation_repository = ConversationRepository(db)
        self.message_repository = MessageRepository(db)

    def create_conversation(self, conversation_create: ConversationCreate) -> ChatConversation:
        conversation_id = generate_rid("chat", "conversation")
        conversation = ChatConversation(id=conversation_id, title=conversation_create.title, user_id=conversation_create.user_id)
        return self.conversation_repository.create(conversation)

    def create_message(self, message_create: MessageCreate) -> MessageResponse:
        message_id = generate_rid("chat", "message")
        message = ChatMessage(id=message_id, content=message_create.content, role=message_create.role, user_id=message_create.user_id, conversation_id=message_create.conversation_id)
        return self.message_repository.create(message)

    def add_message(self, conversation_id: str, content: str, role: str, user_id: str) -> ChatMessage:
        """Add a message to a conversation"""
        message_id = generate_rid("chat", "message")
        message = ChatMessage(
            id=message_id,
            conversation_id=conversation_id,
            content=content,
            role=role,
            user_id=user_id
        )
        return self.message_repository.create(message)

    def get_conversation_messages(self, conversation_id: str) -> List[ChatMessage]:
        """Get all messages in a conversation"""
        return self.db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation_id
        ).order_by(ChatMessage.created_at.asc()).all()

    def get_conversation_context(self, conversation_id: str) -> List[dict]:
        """Get conversation messages formatted for OpenAI API"""
        messages = self.get_conversation_messages(conversation_id)
        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

    def get_or_create_conversation(self, user_id: str) -> ChatConversation:
        """Get existing conversation or create new one"""
        # First, try to get the user's most recent active conversation
        existing_conversation = self.db.query(ChatConversation).filter(
            ChatConversation.user_id == user_id,
            ChatConversation.status == "active"
        ).order_by(ChatConversation.created_at.desc()).first()
        
        if existing_conversation:
            return existing_conversation
        
        # If no active conversation, create a new one
        conversation_id = generate_rid("chat", "conversation")
        new_conversation = ChatConversation(
            id=conversation_id,
            user_id=user_id,
            title="New Chat",  # Default title
            status="active"
        )
        return self.conversation_repository.create(new_conversation)