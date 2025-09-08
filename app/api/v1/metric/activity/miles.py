import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.db.session import get_db
from app.models.auth.user import User
from app.models.metric.activity.miles import ActivityMiles
from app.schemas.metric.activity.miles import (
    ActivityMilesCreate,
    ActivityMilesCreateResponse,
    ActivityMilesDeleteResponse,
    ActivityMilesResponse,
)
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/metric/miles", tags=["metric-miles"])


@router.get("/", response_model=list[ActivityMilesResponse])
async def get_activity_miles(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get activity miles data"""
    try:
        query = db.query(ActivityMiles).filter(ActivityMiles.user_id == current_user.id)

        # Apply date filters if provided
        if start_date:
            query = query.filter(ActivityMiles.date >= start_date)
        if end_date:
            query = query.filter(ActivityMiles.date <= end_date)

        records = query.order_by(ActivityMiles.date.desc()).all()

        logger.info(
            f"Retrieved {len(records)} activity miles records for {current_user.id}"
        )
        return records

    except Exception as e:
        logger.error(f"Error retrieving activity miles: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving data: {str(e)}",
        )


@router.get("/{record_id}", response_model=ActivityMilesResponse)
async def get_activity_mile_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific activity miles record by ID"""
    try:
        record = (
            db.query(ActivityMiles)
            .filter(
                ActivityMiles.id == record_id,
                ActivityMiles.user_id == current_user.id,
            )
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity miles record not found",
            )

        logger.info(
            f"Retrieved activity miles record {record_id} for {current_user.id}"
        )
        return record

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving activity miles record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving record: {str(e)}",
        )


@router.post("/", response_model=ActivityMilesCreateResponse)
async def create_or_update_activity_miles_record(
    miles_data: ActivityMilesCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create or update an activity miles record (upsert)"""
    try:
        # Check if record already exists for this date and source
        existing_record = (
            db.query(ActivityMiles)
            .filter(
                ActivityMiles.user_id == current_user.id,
                ActivityMiles.date == miles_data.date,
                ActivityMiles.source == miles_data.source,
            )
            .first()
        )

        if existing_record:
            # Update existing record
            if miles_data.miles is not None:
                existing_record.miles = miles_data.miles
            if miles_data.notes is not None:
                existing_record.notes = miles_data.notes

            db.commit()
            db.refresh(existing_record)

            logger.info(f"Updated activity miles record for {current_user.id}")
            return ActivityMilesCreateResponse(
                message="Activity miles record updated successfully",
                record=existing_record,
            )
        else:
            # Create new activity miles record
            new_record = ActivityMiles(
                id=generate_rid("metric", "activity_miles"),
                user_id=current_user.id,
                date=miles_data.date,
                miles=miles_data.miles,
                source=miles_data.source,
                notes=miles_data.notes,
            )
            db.add(new_record)
            db.commit()
            db.refresh(new_record)

            logger.info(f"Created activity miles record for {current_user.id}")
            return ActivityMilesCreateResponse(
                message="Activity miles record created successfully", record=new_record
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating/updating activity miles record: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating/updating record: {str(e)}",
        )


@router.delete("/{record_id}", response_model=ActivityMilesDeleteResponse)
async def delete_activity_miles_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete an activity miles record"""
    try:
        # Find and delete the record
        record = (
            db.query(ActivityMiles)
            .filter(
                ActivityMiles.id == record_id,
                ActivityMiles.user_id == current_user.id,
            )
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity miles record not found to delete",
            )

        db.delete(record)
        db.commit()

        logger.info(f"Deleted activity miles record {record_id} for {current_user.id}")
        return ActivityMilesDeleteResponse(
            message="Activity miles record deleted successfully", deleted_count=1
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting activity miles record: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting record: {str(e)}",
        )
