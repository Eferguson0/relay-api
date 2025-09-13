import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.db.session import get_db
from app.models.auth.user import AuthUser
from app.models.goal.macros import GoalMacros
from app.schemas.goal.macros import (
    GoalMacrosBulkCreate,
    GoalMacrosBulkCreateResponse,
    GoalMacrosDeleteResponse,
    GoalMacrosResponse,
)
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/macros", tags=["goal-macros"])


@router.get("/", response_model=list[GoalMacrosResponse])
async def get_macro_goals(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
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


@router.post("/bulk", response_model=GoalMacrosBulkCreateResponse)
async def create_or_update_multiple_macro_goals(
    bulk_data: GoalMacrosBulkCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Create or update multiple macro goals (bulk upsert)"""
    try:
        created_count = 0
        updated_count = 0
        processed_records = []

        for goal_data in bulk_data.records:
            # Check if user already has a macro goal
            existing_goal = (
                db.query(GoalMacros)
                .filter(GoalMacros.user_id == current_user.id)
                .one_or_none()
            )

            if existing_goal:
                # Update existing goal
                if goal_data.calories is not None:
                    setattr(existing_goal, "calories", goal_data.calories)
                if goal_data.protein is not None:
                    setattr(existing_goal, "protein", goal_data.protein)
                if goal_data.carbs is not None:
                    setattr(existing_goal, "carbs", goal_data.carbs)
                if goal_data.fat is not None:
                    setattr(existing_goal, "fat", goal_data.fat)
                if goal_data.calorie_deficit is not None:
                    setattr(existing_goal, "calorie_deficit", goal_data.calorie_deficit)
                processed_records.append(existing_goal)
                updated_count += 1
            else:
                # Create new macro goal record
                new_goal = GoalMacros(
                    id=generate_rid("goal", "macros"),
                    user_id=current_user.id,
                    calories=goal_data.calories,
                    protein=goal_data.protein,
                    carbs=goal_data.carbs,
                    fat=goal_data.fat,
                    calorie_deficit=goal_data.calorie_deficit,
                )
                db.add(new_goal)
                processed_records.append(new_goal)
                created_count += 1

        # Commit all changes at once
        db.commit()

        logger.info(
            f"Bulk processed {len(bulk_data.records)} macro goals for {current_user.id}: "
            f"{created_count} created, {updated_count} updated"
        )

        return GoalMacrosBulkCreateResponse(
            message=f"Bulk operation completed: {created_count} created, {updated_count} updated",
            created_count=created_count,
            updated_count=updated_count,
            total_processed=len(bulk_data.records),
            records=processed_records,
        )

    except Exception as e:
        logger.error(f"Error in bulk upsert of macro goals: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in bulk upsert: {str(e)}",
        )


@router.delete("/{goal_id}", response_model=GoalMacrosDeleteResponse)
async def delete_macro_goal(
    goal_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
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
