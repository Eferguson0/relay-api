import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.goals import GoalWeight
from app.models.user import User
from app.schemas.goals import (
    GoalWeightCreate,
    GoalWeightCreateResponse,
    GoalWeightDeleteResponse,
    GoalWeightResponse,
    GoalWeightUpdate,
    GoalWeightUpdateResponse,
)
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["goals"])


@router.post("/goals/weight", response_model=GoalWeightCreateResponse)
async def create_goal_weight(
    goal_data: GoalWeightCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new weight goal"""
    try:
        # Check if user already has a weight goal
        existing_goal = (
            db.query(GoalWeight).filter(GoalWeight.user_id == current_user.id).first()
        )

        if existing_goal:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has a weight goal. Use PUT to update it.",
            )

        # Create new goal weight record
        new_goal = GoalWeight(
            user_id=current_user.id,
            weight=goal_data.weight,
            body_fat_percentage=goal_data.body_fat_percentage,
            muscle_mass_percentage=goal_data.muscle_mass_percentage,
        )
        db.add(new_goal)
        db.commit()
        db.refresh(new_goal)

        logger.info(f"Created weight goal for {current_user.id}")
        return GoalWeightCreateResponse(
            message="Weight goal created successfully", goal=new_goal
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating weight goal: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating goal: {str(e)}",
        )


@router.get("/goals/weight", response_model=GoalWeightResponse)
async def get_goal_weight(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get current user's weight goal"""
    try:
        goal = (
            db.query(GoalWeight).filter(GoalWeight.user_id == current_user.id).first()
        )

        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No weight goal found for user",
            )

        logger.info(f"Retrieved weight goal for {current_user.id}")
        return goal

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving weight goal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving goal: {str(e)}",
        )


@router.put("/goals/weight", response_model=GoalWeightUpdateResponse)
async def update_goal_weight(
    goal_data: GoalWeightUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update current user's weight goal"""
    try:
        # Find existing goal
        goal = (
            db.query(GoalWeight).filter(GoalWeight.user_id == current_user.id).first()
        )

        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No weight goal found to update",
            )

        # Update fields if provided
        if goal_data.weight is not None:
            goal.weight = goal_data.weight
        if goal_data.body_fat_percentage is not None:
            goal.body_fat_percentage = goal_data.body_fat_percentage
        if goal_data.muscle_mass_percentage is not None:
            goal.muscle_mass_percentage = goal_data.muscle_mass_percentage

        db.commit()
        db.refresh(goal)

        logger.info(f"Updated weight goal for {current_user.id}")
        return GoalWeightUpdateResponse(
            message="Weight goal updated successfully", goal=goal
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating weight goal: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating goal: {str(e)}",
        )


@router.delete("/goals/weight", response_model=GoalWeightDeleteResponse)
async def delete_goal_weight(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete current user's weight goal"""
    try:
        # Find and delete the goal
        goal = (
            db.query(GoalWeight).filter(GoalWeight.user_id == current_user.id).first()
        )

        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No weight goal found to delete",
            )

        db.delete(goal)
        db.commit()

        logger.info(f"Deleted weight goal for {current_user.id}")
        return GoalWeightDeleteResponse(
            message="Weight goal deleted successfully", deleted_count=1
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting weight goal: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting goal: {str(e)}",
        )
