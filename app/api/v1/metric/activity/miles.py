import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.db.session import get_db
from app.models.auth.user import AuthUser
from app.models.metric.activity.miles import ActivityMiles
from app.schemas.metric.activity.miles import (
    ActivityMilesBulkCreate,
    ActivityMilesBulkCreateResponse,
    ActivityMilesDeleteResponse,
    ActivityMilesResponse,
)
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/miles", tags=["metric-miles"])


@router.get("/", response_model=list[ActivityMilesResponse])
async def get_activity_miles(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
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
    current_user: AuthUser = Depends(get_current_active_user),
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


@router.post("/bulk", response_model=ActivityMilesBulkCreateResponse)
async def create_or_update_multiple_activity_miles_records(
    bulk_data: ActivityMilesBulkCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Create or update multiple activity miles records (bulk upsert)"""
    try:
        created_count = 0
        updated_count = 0
        processed_records = []

        for miles_data in bulk_data.records:
            # Check if record already exists for this date and source
            existing_record = (
                db.query(ActivityMiles)
                .filter(
                    ActivityMiles.user_id == current_user.id,
                    ActivityMiles.date_hour == miles_data.date_hour,
                    ActivityMiles.source == miles_data.source,
                )
                .one_or_none()
            )

            if existing_record:
                # Update existing record
                if miles_data.miles is not None:
                    setattr(existing_record, "miles", miles_data.miles)
                if miles_data.activity_type is not None:
                    setattr(existing_record, "activity_type", miles_data.activity_type)
                setattr(existing_record, "updated_at", datetime.utcnow())
                processed_records.append(existing_record)
                updated_count += 1
            else:
                # Create new activity miles record
                new_record = ActivityMiles(
                    id=generate_rid("metric", "activity_miles"),
                    user_id=current_user.id,
                    date_hour=miles_data.date_hour,
                    miles=miles_data.miles,
                    activity_type=miles_data.activity_type,
                    source=miles_data.source,
                )
                db.add(new_record)
                processed_records.append(new_record)
                created_count += 1

        # Commit all changes at once
        db.commit()

        logger.info(
            f"Bulk processed {len(bulk_data.records)} activity miles records for {current_user.id}: "
            f"{created_count} created, {updated_count} updated"
        )

        return ActivityMilesBulkCreateResponse(
            message=f"Bulk operation completed: {created_count} created, {updated_count} updated",
            created_count=created_count,
            updated_count=updated_count,
            total_processed=len(bulk_data.records),
            records=processed_records,
        )

    except Exception as e:
        logger.error(f"Error in bulk upsert of activity miles records: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in bulk upsert: {str(e)}",
        )


@router.delete("/{record_id}", response_model=ActivityMilesDeleteResponse)
async def delete_activity_miles_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
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
