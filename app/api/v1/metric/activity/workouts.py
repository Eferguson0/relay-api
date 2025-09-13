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


@router.get("/", response_model=list[ActivityWorkoutsResponse])
async def get_activity_workouts(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Get activity workouts data"""
    try:
        query = db.query(ActivityWorkouts).filter(
            ActivityWorkouts.user_id == current_user.id
        )

        # Apply date filters if provided
        if start_date:
            query = query.filter(ActivityWorkouts.workout_date >= start_date)
        if end_date:
            query = query.filter(ActivityWorkouts.workout_date <= end_date)

        records = query.order_by(ActivityWorkouts.workout_date.desc()).all()

        logger.info(
            f"Retrieved {len(records)} activity workouts records for {current_user.id}"
        )
        return records

    except Exception as e:
        logger.error(f"Error retrieving activity workouts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving data: {str(e)}",
        )


@router.get("/{record_id}", response_model=ActivityWorkoutsResponse)
async def get_activity_workout_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Get a specific activity workout record by ID"""
    try:
        record = (
            db.query(ActivityWorkouts)
            .filter(
                ActivityWorkouts.id == record_id,
                ActivityWorkouts.user_id == current_user.id,
            )
            .first()
        )

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


@router.post("/bulk", response_model=ActivityWorkoutsBulkCreateResponse)
async def create_or_update_multiple_workout_records(
    bulk_data: ActivityWorkoutsBulkCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Create or update multiple workout records (bulk upsert)"""
    try:
        created_count = 0
        updated_count = 0
        processed_records = []

        for workout_data in bulk_data.records:
            # Check if record already exists for this date and source
            existing_record = (
                db.query(ActivityWorkouts)
                .filter(
                    ActivityWorkouts.user_id == current_user.id,
                    ActivityWorkouts.date == workout_data.date,
                    ActivityWorkouts.source == workout_data.source,
                )
                .one_or_none()
            )

            if existing_record:
                # Update existing record
                if workout_data.workout_name is not None:
                    setattr(existing_record, "workout_name", workout_data.workout_name)
                if workout_data.workout_type is not None:
                    setattr(existing_record, "workout_type", workout_data.workout_type)
                if workout_data.duration_minutes is not None:
                    setattr(
                        existing_record,
                        "duration_minutes",
                        workout_data.duration_minutes,
                    )
                if workout_data.calories_burned is not None:
                    setattr(
                        existing_record, "calories_burned", workout_data.calories_burned
                    )
                if workout_data.distance_miles is not None:
                    setattr(
                        existing_record, "distance_miles", workout_data.distance_miles
                    )
                if workout_data.avg_heart_rate is not None:
                    setattr(
                        existing_record, "avg_heart_rate", workout_data.avg_heart_rate
                    )
                if workout_data.max_heart_rate is not None:
                    setattr(
                        existing_record, "max_heart_rate", workout_data.max_heart_rate
                    )
                if workout_data.intensity is not None:
                    setattr(existing_record, "intensity", workout_data.intensity)
                if workout_data.notes is not None:
                    setattr(existing_record, "notes", workout_data.notes)
                setattr(existing_record, "updated_at", datetime.utcnow())
                processed_records.append(existing_record)
                updated_count += 1
            else:
                # Create new workout record
                new_record = ActivityWorkouts(
                    id=generate_rid("metric", "activity_workouts"),
                    user_id=current_user.id,
                    date=workout_data.date,
                    workout_name=workout_data.workout_name,
                    workout_type=workout_data.workout_type,
                    duration_minutes=workout_data.duration_minutes,
                    calories_burned=workout_data.calories_burned,
                    distance_miles=workout_data.distance_miles,
                    avg_heart_rate=workout_data.avg_heart_rate,
                    max_heart_rate=workout_data.max_heart_rate,
                    intensity=workout_data.intensity,
                    source=workout_data.source,
                    notes=workout_data.notes,
                )
                db.add(new_record)
                processed_records.append(new_record)
                created_count += 1

        # Commit all changes at once
        db.commit()

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


@router.delete("/{record_id}", response_model=ActivityWorkoutsDeleteResponse)
async def delete_activity_workout_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Delete an activity workout record"""
    try:
        # Find and delete the record
        record = (
            db.query(ActivityWorkouts)
            .filter(
                ActivityWorkouts.id == record_id,
                ActivityWorkouts.user_id == current_user.id,
            )
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity workout record not found to delete",
            )

        db.delete(record)
        db.commit()

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
