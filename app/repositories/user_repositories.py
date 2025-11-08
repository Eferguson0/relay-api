from datetime import datetime

from fastapi import HTTPException, status
from typing import Optional
from sqlalchemy.orm import Session
from app.models.auth.user import AuthUser
from app.schemas.auth.user import UserUpdate

# TODO: Reconcile transaction boundaries (commit/rollback) between services and repositories.
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

    def update(self, user_id: str, update_data: UserUpdate) -> AuthUser:
        """Update user profile"""
        user = self.db.query(AuthUser).filter(AuthUser.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        user.email = update_data.email
        user.full_name = update_data.full_name
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: str) -> AuthUser:
        """Delete user"""
        user = self.db.query(AuthUser).filter(AuthUser.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        self.db.delete(user)
        self.db.commit()
        return user