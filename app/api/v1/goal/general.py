import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.db.session import get_db
from app.models.auth.user import User
from app.models.goal.general import GoalGeneral
from app.schemas.goal.general import (
    GoalGeneralCreate,
    GoalGeneralCreateResponse,
    GoalGeneralDeleteResponse,
    GoalGeneralResponse,
)
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/goal/general", tags=["goal-general"])


@router.post("/", response_model=GoalGeneralCreateResponse)
async def create_or_update_general_goal(
    goal_data: GoalGeneralCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create or update a general goal (upsert)"""
    try:
        # Check if user already has a general goal
        existing_goal = (
            db.query(GoalGeneral).filter(GoalGeneral.user_id == current_user.id).first()
        )

        if existing_goal:
            # Update existing goal
            if goal_data.target_weight is not None:
                existing_goal.target_weight = goal_data.target_weight
            if goal_data.target_body_fat is not None:
                existing_goal.target_body_fat = goal_data.target_body_fat
            if goal_data.target_muscle_mass is not None:
                existing_goal.target_muscle_mass = goal_data.target_muscle_mass
            if goal_data.target_calories is not None:
                existing_goal.target_calories = goal_data.target_calories
            if goal_data.target_protein is not None:
                existing_goal.target_protein = goal_data.target_protein
            if goal_data.target_carbs is not None:
                existing_goal.target_carbs = goal_data.target_carbs
            if goal_data.target_fat is not None:
                existing_goal.target_fat = goal_data.target_fat
            if goal_data.notes is not None:
                existing_goal.notes = goal_data.notes

            db.commit()
            db.refresh(existing_goal)

            logger.info(f"Updated general goal for {current_user.id}")
            return GoalGeneralCreateResponse(
                message="General goal updated successfully", goal=existing_goal
            )
        else:
            # Create new general goal record
            new_goal = GoalGeneral(
                id=generate_rid("goal", "general"),
                user_id=current_user.id,
                target_weight=goal_data.target_weight,
                target_body_fat=goal_data.target_body_fat,
                target_muscle_mass=goal_data.target_muscle_mass,
                target_calories=goal_data.target_calories,
                target_protein=goal_data.target_protein,
                target_carbs=goal_data.target_carbs,
                target_fat=goal_data.target_fat,
                notes=goal_data.notes,
            )
            db.add(new_goal)
            db.commit()
            db.refresh(new_goal)

            logger.info(f"Created general goal for {current_user.id}")
            return GoalGeneralCreateResponse(
                message="General goal created successfully", goal=new_goal
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating/updating general goal: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating/updating goal: {str(e)}",
        )


@router.get("/", response_model=GoalGeneralResponse)
async def get_general_goal(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get current user's general goal"""
    try:
        goal = (
            db.query(GoalGeneral).filter(GoalGeneral.user_id == current_user.id).first()
        )

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


@router.delete("/", response_model=GoalGeneralDeleteResponse)
async def delete_general_goal(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete current user's general goal"""
    try:
        # Find and delete the goal
        goal = (
            db.query(GoalGeneral).filter(GoalGeneral.user_id == current_user.id).first()
        )

        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No general goal found to delete",
            )

        db.delete(goal)
        db.commit()

        logger.info(f"Deleted general goal for {current_user.id}")
        return GoalGeneralDeleteResponse(
            message="General goal deleted successfully", deleted_count=1
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting general goal: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting goal: {str(e)}",
        )
