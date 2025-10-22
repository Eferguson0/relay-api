import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.auth.user import AuthUser
from app.models.goal.macros import GoalMacros
from app.schemas.goal.macros import (
    GoalMacrosCreate,
    GoalMacrosCreateResponse,
    GoalMacrosDeleteResponse,
    GoalMacrosResponse,
)
from app.services.auth_service import get_current_active_user
from app.services.goal_service import GoalService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/macros", tags=["goal-macros"])


@router.get("/",
    response_model=GoalMacrosResponse,
    summary="Get current user's macro goal",
    description="Get the current user's macro goal",
    responses={
        200: {"description": "Macro goal retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "No macro goal found for user"},
        500: {"description": "Internal server error"},
    }
)
async def get_macro_goal(
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Get macro goal for the user"""
    try:
        goal_service = GoalService(db)
        goal = goal_service.get_macro_goal(current_user.id)

        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No macro goal found for user",
            )


        logger.info(f"Retrieved macro goal for {current_user.id}")
        return goal

    except Exception as e:
        logger.error(f"Error retrieving macro goal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving macro goal: {str(e)}",
        )


@router.post("/",
    response_model=GoalMacrosCreateResponse,
    summary="Create or update a macro goal endpoint",
    description="Create or update a macro goal",
    responses={
        200: {"description": "Macro goal created or updated successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        500: {"description": "Internal server error"},
    }
)
async def create_or_update_macro_goal(
    goal_data: GoalMacrosCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Create or update a macro goal"""
    try:
        goal_service = GoalService(db)
        result = goal_service.create_or_update_macro_goal(goal_data, current_user.id)

        logger.info(f"Created or updated macro goal for {current_user.id}")
        return result

    except Exception as e:
        logger.error(f"Error in creating or updating macro goal: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in creating or updating macro goal: {str(e)}",
        )


@router.delete("/",
    response_model=GoalMacrosDeleteResponse,
    summary="Delete a macro goal endpoint",
    description="Delete a macro goal",
    responses={
        200: {"description": "Macro goal deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "No macro goal found to delete"},
        500: {"description": "Internal server error"},
    }
)
async def delete_macro_goal(
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Delete a specific macro goal"""

    try:
        goal_service = GoalService(db)
        result = goal_service.delete_macro_goal(current_user.id)
        return result

    except Exception as e:
        logger.error(f"Error deleting macro goal: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting macro goal: {str(e)}",
        )
