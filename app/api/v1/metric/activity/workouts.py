import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.db.session import get_db
from app.models.auth.user import AuthUser
from app.models.metric.activity.workouts import ActivityWorkouts
from app.schemas.metric.activity.workouts import (
    ActivityWorkoutsBulkCreate,
    ActivityWorkoutsBulkCreateResponse,
    ActivityWorkoutsDeleteResponse,
    ActivityWorkoutsResponse,
)
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workouts", tags=["metric-workouts"])


@router.get("/",
    response_model=list[ActivityWorkoutsResponse],
    summary="Get activity workouts data endpoint",
    description="Get activity workouts data",
    responses={
        200: {"description": "Activity workouts data retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Activity workouts data not found"},
    },
)
async def get_activity_workouts(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Get activity workouts data"""
    try:
        
        metrics_service = MetricsService(db)
        workouts_data = metrics_service.get_workouts_data(current_user.id, start_date, end_date)

        if not workouts_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity workouts data not found",
            )

        logger.info(
            f"Retrieved {len(workouts_data)} activity workouts records for {current_user.id}"
        )
        return workouts_data

    except Exception as e:
        logger.error(f"Error retrieving activity workouts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving data: {str(e)}",
        )


@router.get("/{record_id}",
    response_model=ActivityWorkoutsResponse,
    summary="Get a specific activity workout record by ID endpoint",
    description="Get a specific activity workout record by ID",
    responses={
        200: {"description": "Activity workout record retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Activity workout record not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_activity_workout_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Get a specific activity workout record by ID"""
    try:
        
        metrics_service = MetricsService(db)
        record = metrics_service.get_workouts_data_by_id(current_user.id, record_id)

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity workout record not found",
            )

        logger.info(
            f"Retrieved activity workout record {record_id} for {current_user.id}"
        )
        return record

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving activity workout record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving record: {str(e)}",
        )


@router.post("/bulk",
    response_model=ActivityWorkoutsBulkCreateResponse,
    summary="Create or update multiple workout records (bulk upsert) endpoint",
    description="Create or update multiple workout records (bulk upsert)",
    responses={
        200: {"description": "Workout records created or updated successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Activity workout record not found"},
        500: {"description": "Internal server error"},
    },
)
async def create_or_update_multiple_workout_records(
    bulk_data: ActivityWorkoutsBulkCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Create or update multiple workout records (bulk upsert)"""
    try:
        
        metrics_service = MetricsService(db)
        processed_records, created_count, updated_count = metrics_service.create_or_update_multiple_workouts_records(bulk_data, current_user.id)

        if not processed_records:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity workout record not found",
            )

        logger.info(
            f"Bulk processed {len(bulk_data.records)} workout records for {current_user.id}: "
            f"{created_count} created, {updated_count} updated"
        )

        return ActivityWorkoutsBulkCreateResponse(
            message=f"Bulk operation completed: {created_count} created, {updated_count} updated",
            created_count=created_count,
            updated_count=updated_count,
            total_processed=len(bulk_data.records),
            records=processed_records,
        )

    except Exception as e:
        logger.error(f"Error in bulk upsert of workout records: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in bulk upsert: {str(e)}",
        )


@router.delete("/{record_id}",
    response_model=ActivityWorkoutsDeleteResponse,
    summary="Delete a workout record by ID endpoint",
    description="Delete a workout record by ID",
    responses={
        200: {"description": "Workout record deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Workout record not found to delete"},
        500: {"description": "Internal server error"},
    },
)
async def delete_activity_workout_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Delete an activity workout record"""
    try:
        
        metrics_service = MetricsService(db)
        record = metrics_service.delete_workouts_record(current_user.id, record_id)

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity workout record not found to delete",
            )

        logger.info(
            f"Deleted activity workout record {record_id} for {current_user.id}"
        )
        return ActivityWorkoutsDeleteResponse(
            message="Activity workout record deleted successfully", deleted_count=1
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting activity workout record: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting record: {str(e)}",
        )
