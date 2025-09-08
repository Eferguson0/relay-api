import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.db.session import get_db
from app.models.auth.user import User
from app.models.metric.activity.workouts import ActivityWorkouts
from app.schemas.metric.activity.workouts import (
    ActivityWorkoutsCreate,
    ActivityWorkoutsCreateResponse,
    ActivityWorkoutsDeleteResponse,
    ActivityWorkoutsResponse,
)
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/metric/workouts", tags=["metric-workouts"])


@router.get("/", response_model=list[ActivityWorkoutsResponse])
async def get_activity_workouts(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
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
    current_user: User = Depends(get_current_active_user),
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


@router.post("/", response_model=ActivityWorkoutsCreateResponse)
async def create_or_update_activity_workout_record(
    workout_data: ActivityWorkoutsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create or update an activity workout record (upsert)"""
    try:
        # Check if record already exists for this workout_date and source
        existing_record = (
            db.query(ActivityWorkouts)
            .filter(
                ActivityWorkouts.user_id == current_user.id,
                ActivityWorkouts.workout_date == workout_data.workout_date,
                ActivityWorkouts.source == workout_data.source,
            )
            .first()
        )

        if existing_record:
            # Update existing record
            if workout_data.workout_type is not None:
                existing_record.workout_type = workout_data.workout_type
            if workout_data.duration_minutes is not None:
                existing_record.duration_minutes = workout_data.duration_minutes
            if workout_data.calories_burned is not None:
                existing_record.calories_burned = workout_data.calories_burned
            if workout_data.notes is not None:
                existing_record.notes = workout_data.notes

            db.commit()
            db.refresh(existing_record)

            logger.info(f"Updated activity workout record for {current_user.id}")
            return ActivityWorkoutsCreateResponse(
                message="Activity workout record updated successfully",
                record=existing_record,
            )
        else:
            # Create new activity workout record
            new_record = ActivityWorkouts(
                id=generate_rid("metric", "activity_workouts"),
                user_id=current_user.id,
                workout_date=workout_data.workout_date,
                workout_type=workout_data.workout_type,
                duration_minutes=workout_data.duration_minutes,
                calories_burned=workout_data.calories_burned,
                source=workout_data.source,
                notes=workout_data.notes,
            )
            db.add(new_record)
            db.commit()
            db.refresh(new_record)

            logger.info(f"Created activity workout record for {current_user.id}")
            return ActivityWorkoutsCreateResponse(
                message="Activity workout record created successfully",
                record=new_record,
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating/updating activity workout record: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating/updating record: {str(e)}",
        )


@router.delete("/{record_id}", response_model=ActivityWorkoutsDeleteResponse)
async def delete_activity_workout_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
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
