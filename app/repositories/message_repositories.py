from sqlalchemy.orm import Session

from app.models.chat.message import ChatMessage

# TODO: Reconcile transaction boundaries (commit/rollback) between services and repositories.
class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, message: ChatMessage) -> ChatMessage:
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message