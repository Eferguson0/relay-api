import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.db.session import get_db
from app.models.auth.user import AuthUser
from app.models.goal.general import GoalGeneral
from app.schemas.goal.general import (
    GoalGeneralBulkCreate,
    GoalGeneralBulkCreateResponse,
    GoalGeneralDeleteResponse,
    GoalGeneralResponse,
)
from app.services.auth_service import get_current_active_user
from app.services.goal_service import GoalService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/general", tags=["goal-general"])


@router.get("/",
    response_model=GoalGeneralResponse,
    summary="Get current user's general goal endpoint",
    description="Get the current user's general goal",
    responses={
        200: {"description": "General goal retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "No general goal found for user"},
        500: {"description": "Internal server error"},
    }
)
async def get_general_goal(
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Get current user's general goal"""
    try:
        goal_service = GoalService(db)
        goal = goal_service.get_general_goal(current_user.id)

        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No general goal found for user",
            )

        logger.info(f"Retrieved general goal for {current_user.id}")
        return goal

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving general goal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving goal: {str(e)}",
        )


@router.post("/bulk",
    response_model=GoalGeneralBulkCreateResponse,
    summary="Create or update multiple general goals endpoint",
    description="Create or update multiple general goals",
    responses={
        200: {"description": "General goals created or updated successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "No general goal found for user"},
        500: {"description": "Internal server error"},
    }
)
async def create_or_update_multiple_general_goals(
    bulk_data: GoalGeneralBulkCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Create or update multiple general goals (bulk upsert)"""
    try:
        
        goal_service = GoalService(db)
        result = goal_service.create_or_update_multiple_general_goals(bulk_data, current_user.id)
        return result
        

    except Exception as e:
        logger.error(f"Error in bulk upsert of general goals: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in bulk upsert: {str(e)}",
        )


@router.delete("/",
    response_model=GoalGeneralDeleteResponse,
    summary="Delete current user's general goal endpoint",
    description="Delete the current user's general goal",
    responses={
        200: {"description": "General goal deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "No general goal found for user"},
        500: {"description": "Internal server error"},
    }
)
async def delete_general_goal(
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Delete current user's general goal"""

    try:
        goal_service = GoalService(db)
        result = goal_service.delete_general_goal(current_user.id)
        return result


    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting general goal: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting goal: {str(e)}",
        )
