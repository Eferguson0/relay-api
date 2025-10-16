from typing import Optional
from sqlalchemy.orm import Session
from app.models.auth.user import AuthUser

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user: AuthUser) -> AuthUser:
        """Create a new user in the database"""
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_by_email(self, email: str) -> Optional[AuthUser]:
        """Get user by email"""
        return self.db.query(AuthUser).filter(AuthUser.email == email).first()
    
    def get_by_id(self, user_id: str) -> Optional[AuthUser]:
        """Get user by ID"""
        return self.db.query(AuthUser).filter(AuthUser.id == user_id).first()