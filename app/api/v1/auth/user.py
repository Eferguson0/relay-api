import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.auth.user import AuthUser
from app.schemas.auth.user import UserResponse, UserUpdate, UserDeleteResponse
from app.services.auth_service import AuthService, get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user", tags=["auth-user"])


@router.get("/",
    response_model=UserResponse,
    summary="Get current user profile endpoint",
    description="Get the current user profile",
    responses={
        200: {"description": "User profile retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_current_user_profile(
    current_user: AuthUser = Depends(get_current_active_user),
):
    logger.info(f"User profile requested for: {current_user.email}")
    return current_user


@router.put("/",
    response_model=UserResponse,
    summary="Update current user profile endpoint",
    description="Update the current user profile",
    responses={
        200: {"description": "User profile updated successfully"},
        400: {"description": "Invalid input"},
        403: {"description": "Inactive user"},
        404: {"description": "User not found"},
    }
)
async def update_user_profile(
    update_data: UserUpdate,
    current_user: AuthUser = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    logger.info(f"User profile update requested for: {current_user.email}")
    auth_service = AuthService(db)
    updated_user = auth_service.update_user_profile(current_user.id, update_data)
    return updated_user


@router.delete("/",
    response_model=UserDeleteResponse,
    summary="Delete current user account endpoint",
    description="Delete the current user account",
    responses={
        200: {"description": "User account deleted successfully"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    }
)
async def delete_user_account(
    current_user: AuthUser = Depends(get_current_active_user),
    db: Session = Depends(get_db),    
):
    logger.info(f"User account deletion requested for: {current_user.email}")
    auth_service = AuthService(db)
    deleted_user = auth_service.delete_user(current_user.id)
    return deleted_user
