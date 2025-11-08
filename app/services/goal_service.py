import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.rid import generate_rid
from app.models.goal.general import GoalGeneral
from app.models.goal.macros import GoalMacros
from app.repositories.goal_repositories import GoalRepository
from app.schemas.goal.general import (
    GoalGeneralBulkCreate,
    GoalGeneralBulkCreateResponse,
    GoalGeneralDeleteResponse,
)
from app.schemas.goal.macros import (
    GoalMacrosCreate,
    GoalMacrosCreateResponse,
    GoalMacrosDeleteResponse,
)

logger = logging.getLogger(__name__)

class GoalService:
    def __init__(self, db: Session):
        self.db = db

# General Goal Services

    def get_general_goal(self, user_id: str) -> GoalGeneral:
        goal_repository = GoalRepository(self.db)
        return goal_repository.get_general_goal(user_id)

    def create_or_update_multiple_general_goals(self, bulk_data: GoalGeneralBulkCreate, user_id: str) -> GoalGeneralBulkCreateResponse:
        goal_repository = GoalRepository(self.db)

        created_count = 0
        updated_count = 0
        processed_records = []

        for goal_data in bulk_data.records:
            # Check if user already has a general goal
            existing_goal = goal_repository.get_general_goal(user_id)

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
                updated_goal = goal_repository.update_general_goal(existing_goal)
                processed_records.append(existing_goal)
                updated_count += 1
            else:
                # Create new general goal record
                new_goal = goal_repository.create_general_goal(GoalGeneral(
                    id=generate_rid("goal", "general"),
                    user_id=user_id,
                    goal_description=goal_data.goal_description,
                    target_date=goal_data.target_date,
                    target_weight=goal_data.target_weight,
                    target_body_fat_percentage=goal_data.target_body_fat_percentage,
                    target_muscle_mass_percentage=goal_data.target_muscle_mass_percentage,
                ))
                processed_records.append(new_goal)
                created_count += 1


        logger.info(
            f"Bulk processed {len(bulk_data.records)} general goals for {user_id}: "
            f"{created_count} created, {updated_count} updated"
        )
        
        return GoalGeneralBulkCreateResponse(
            message=f"Bulk operation completed: {created_count} created, {updated_count} updated",
            created_count=created_count,
            updated_count=updated_count,
            total_processed=len(bulk_data.records),
            records=processed_records,
        )


    def delete_general_goal(self, user_id: str) -> GoalGeneralDeleteResponse:
        goal_repository = GoalRepository(self.db)
        goal = goal_repository.delete_general_goal(user_id)

        if not goal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No general goal found to delete")
        logger.info(f"Deleted general goal for {user_id}")
        return GoalGeneralDeleteResponse(
            message="General goal deleted successfully",
            deleted_count=1
        )

# Macro Goal Services

    def get_macro_goal(self, user_id: str) -> GoalMacros:
        goal_repository = GoalRepository(self.db)   
        goal = goal_repository.get_macro_goal(user_id)

        if not goal:
            return None

        logger.info(f"Retrieved macro goal for {user_id}")
        return goal


    def create_or_update_macro_goal(self, goal_data: GoalMacrosCreate, user_id: str) -> GoalMacrosCreateResponse:
        goal_repository = GoalRepository(self.db)
        existing_goal = goal_repository.get_macro_goal(user_id)

        if existing_goal:
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
            setattr(existing_goal, "updated_at", datetime.now(timezone.utc))
            existing_goal = goal_repository.update_macro_goal(existing_goal)
            return GoalMacrosCreateResponse(
                message="Macro goal updated successfully",
                goal=existing_goal
            )
        else:
            new_goal = goal_repository.create_macro_goal(GoalMacros(
                id=generate_rid("goal", "macros"),
                user_id=user_id,
                calories=goal_data.calories,
                protein=goal_data.protein,
                carbs=goal_data.carbs,
                fat=goal_data.fat,
                calorie_deficit=goal_data.calorie_deficit,
            ))
            return GoalMacrosCreateResponse(
                message="Macro goal created successfully",
                goal=new_goal
            )


    def delete_macro_goal(self, user_id: str) -> GoalMacrosDeleteResponse:
        goal_repository = GoalRepository(self.db)
        goal = goal_repository.delete_macro_goal(user_id)

        if not goal:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No macro goal found to delete")
        logger.info(f"Deleted macro goal for {user_id}")
        return GoalMacrosDeleteResponse(
            message="Macro goal deleted successfully",
            deleted_count=1
        )
