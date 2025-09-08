import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.auth.user import User
from app.models.goal.weight import GoalWeight
from app.schemas.goal.weight import (
    GoalWeightCreate,
    GoalWeightCreateResponse,
    GoalWeightDeleteResponse,
    GoalWeightResponse,
)
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/goal/weight", tags=["goal-weight"])


@router.post("/", response_model=GoalWeightCreateResponse)
async def create_or_update_goal_weight(
    goal_data: GoalWeightCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create or update a weight goal (upsert)"""
    try:
        # Check if user already has a weight goal
        existing_goal = (
            db.query(GoalWeight).filter(GoalWeight.user_id == current_user.id).first()
        )

        if existing_goal:
            # Update existing goal
            if goal_data.weight is not None:
                existing_goal.weight = goal_data.weight
            if goal_data.body_fat_percentage is not None:
                existing_goal.body_fat_percentage = goal_data.body_fat_percentage
            if goal_data.muscle_mass_percentage is not None:
                existing_goal.muscle_mass_percentage = goal_data.muscle_mass_percentage

            db.commit()
            db.refresh(existing_goal)

            logger.info(f"Updated weight goal for {current_user.id}")
            return GoalWeightCreateResponse(
                message="Weight goal updated successfully", goal=existing_goal
            )
        else:
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
        logger.error(f"Error creating/updating weight goal: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating/updating goal: {str(e)}",
        )


@router.get("/", response_model=GoalWeightResponse)
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


@router.delete("/", response_model=GoalWeightDeleteResponse)
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
