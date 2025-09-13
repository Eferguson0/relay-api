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

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/general", tags=["goal-general"])


@router.get("/", response_model=GoalGeneralResponse)
async def get_general_goal(
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
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


@router.post("/bulk", response_model=GoalGeneralBulkCreateResponse)
async def create_or_update_multiple_general_goals(
    bulk_data: GoalGeneralBulkCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Create or update multiple general goals (bulk upsert)"""
    try:
        created_count = 0
        updated_count = 0
        processed_records = []

        for goal_data in bulk_data.records:
            # Check if user already has a general goal
            existing_goal = (
                db.query(GoalGeneral)
                .filter(GoalGeneral.user_id == current_user.id)
                .one_or_none()
            )

            if existing_goal:
                # Update existing goal
                if goal_data.goal_description is not None:
                    setattr(
                        existing_goal, "goal_description", goal_data.goal_description
                    )
                if goal_data.target_date is not None:
                    setattr(existing_goal, "target_date", goal_data.target_date)
                if goal_data.target_weight is not None:
                    setattr(existing_goal, "target_weight", goal_data.target_weight)
                if goal_data.target_body_fat_percentage is not None:
                    setattr(
                        existing_goal,
                        "target_body_fat_percentage",
                        goal_data.target_body_fat_percentage,
                    )
                if goal_data.target_muscle_mass_percentage is not None:
                    setattr(
                        existing_goal,
                        "target_muscle_mass_percentage",
                        goal_data.target_muscle_mass_percentage,
                    )
                processed_records.append(existing_goal)
                updated_count += 1
            else:
                # Create new general goal record
                new_goal = GoalGeneral(
                    id=generate_rid("goal", "general"),
                    user_id=current_user.id,
                    goal_description=goal_data.goal_description,
                    target_date=goal_data.target_date,
                    target_weight=goal_data.target_weight,
                    target_body_fat_percentage=goal_data.target_body_fat_percentage,
                    target_muscle_mass_percentage=goal_data.target_muscle_mass_percentage,
                )
                db.add(new_goal)
                processed_records.append(new_goal)
                created_count += 1

        # Commit all changes at once
        db.commit()

        logger.info(
            f"Bulk processed {len(bulk_data.records)} general goals for {current_user.id}: "
            f"{created_count} created, {updated_count} updated"
        )

        return GoalGeneralBulkCreateResponse(
            message=f"Bulk operation completed: {created_count} created, {updated_count} updated",
            created_count=created_count,
            updated_count=updated_count,
            total_processed=len(bulk_data.records),
            records=processed_records,
        )

    except Exception as e:
        logger.error(f"Error in bulk upsert of general goals: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in bulk upsert: {str(e)}",
        )


@router.delete("/", response_model=GoalGeneralDeleteResponse)
async def delete_general_goal(
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
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
