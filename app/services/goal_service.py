import logging

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.rid import generate_rid
from app.models.goal.general import GoalGeneral
from app.repositories.goal_repositories import GoalRepository
from app.schemas.goal.general import GoalGeneralBulkCreate, GoalGeneralBulkCreateResponse, GoalGeneralDeleteResponse

logger = logging.getLogger(__name__)

class GoalService:
    def __init__(self, db: Session):
        self.db = db

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
