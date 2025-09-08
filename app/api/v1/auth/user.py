import logging

from fastapi import APIRouter, Depends

from app.models.auth.user import User
from app.schemas.auth.user import UserResponse
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth/user", tags=["auth-user"])


@router.get("/", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
):
    """Get current user profile"""
    logger.info(f"User profile requested for: {current_user.email}")
    return current_user


@router.put("/", response_model=UserResponse)
async def update_user_profile(
    current_user: User = Depends(get_current_active_user),
):
    """Update current user profile"""
    # TODO: Implement user profile update functionality
    logger.info(f"User profile update requested for: {current_user.email}")
    return {"message": "Update user profile endpoint - to be implemented"}


@router.delete("/")
async def delete_user_account(
    current_user: User = Depends(get_current_active_user),
):
    """Delete current user account"""
    # TODO: Implement user account deletion functionality
    logger.info(f"User account deletion requested for: {current_user.email}")
    return {"message": "Delete user account endpoint - to be implemented"}
