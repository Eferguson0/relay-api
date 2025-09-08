import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.db.session import get_db
from app.models.auth.user import User
from app.models.goal.macros import GoalMacros
from app.schemas.goal.macros import (
    GoalMacrosCreate,
    GoalMacrosCreateResponse,
    GoalMacrosDeleteResponse,
    GoalMacrosResponse,
)
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/goal/macros", tags=["goal-macros"])


@router.post("/", response_model=GoalMacrosCreateResponse)
async def create_or_update_macro_goal(
    goal_data: GoalMacrosCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create or update a macro goal (upsert)"""
    try:
        # Check if user already has a macro goal for this date_hour
        existing_goal = (
            db.query(GoalMacros)
            .filter(
                GoalMacros.user_id == current_user.id,
                GoalMacros.date_hour == goal_data.date_hour,
            )
            .first()
        )

        if existing_goal:
            # Update existing goal
            if goal_data.calories is not None:
                existing_goal.calories = goal_data.calories
            if goal_data.protein is not None:
                existing_goal.protein = goal_data.protein
            if goal_data.carbs is not None:
                existing_goal.carbs = goal_data.carbs
            if goal_data.fat is not None:
                existing_goal.fat = goal_data.fat
            if goal_data.notes is not None:
                existing_goal.notes = goal_data.notes

            db.commit()
            db.refresh(existing_goal)

            logger.info(
                f"Updated macro goal for {current_user.id} at {goal_data.date_hour}"
            )
            return GoalMacrosCreateResponse(
                message="Macro goal updated successfully", goal=existing_goal
            )
        else:
            # Create new macro goal record
            new_goal = GoalMacros(
                id=generate_rid("goal", "macros"),
                user_id=current_user.id,
                date_hour=goal_data.date_hour,
                calories=goal_data.calories,
                protein=goal_data.protein,
                carbs=goal_data.carbs,
                fat=goal_data.fat,
                notes=goal_data.notes,
            )
            db.add(new_goal)
            db.commit()
            db.refresh(new_goal)

            logger.info(
                f"Created macro goal for {current_user.id} at {goal_data.date_hour}"
            )
            return GoalMacrosCreateResponse(
                message="Macro goal created successfully", goal=new_goal
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating/updating macro goal: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating/updating goal: {str(e)}",
        )


@router.get("/", response_model=list[GoalMacrosResponse])
async def get_macro_goals(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get macro goals for the user with optional date filtering"""
    try:
        query = db.query(GoalMacros).filter(GoalMacros.user_id == current_user.id)

        # Apply date filters if provided
        if start_date:
            query = query.filter(GoalMacros.date_hour >= start_date)
        if end_date:
            query = query.filter(GoalMacros.date_hour <= end_date)

        goals = query.order_by(GoalMacros.date_hour.desc()).all()

        logger.info(f"Retrieved {len(goals)} macro goals for {current_user.id}")
        return goals

    except Exception as e:
        logger.error(f"Error retrieving macro goals: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving goals: {str(e)}",
        )


@router.get("/{goal_id}", response_model=GoalMacrosResponse)
async def get_macro_goal(
    goal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific macro goal by ID"""
    try:
        goal = (
            db.query(GoalMacros)
            .filter(
                GoalMacros.id == goal_id,
                GoalMacros.user_id == current_user.id,
            )
            .first()
        )

        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Macro goal not found",
            )

        logger.info(f"Retrieved macro goal {goal_id} for {current_user.id}")
        return goal

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving macro goal: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving goal: {str(e)}",
        )


@router.delete("/{goal_id}", response_model=GoalMacrosDeleteResponse)
async def delete_macro_goal(
    goal_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a specific macro goal"""
    try:
        # Find and delete the goal
        goal = (
            db.query(GoalMacros)
            .filter(
                GoalMacros.id == goal_id,
                GoalMacros.user_id == current_user.id,
            )
            .first()
        )

        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Macro goal not found to delete",
            )

        db.delete(goal)
        db.commit()

        logger.info(f"Deleted macro goal {goal_id} for {current_user.id}")
        return GoalMacrosDeleteResponse(
            message="Macro goal deleted successfully", deleted_count=1
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting macro goal: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting goal: {str(e)}",
        )
