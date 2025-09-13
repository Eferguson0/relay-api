import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.db.session import get_db
from app.models.auth.user import AuthUser
from app.models.metric.activity.steps import ActivitySteps
from app.schemas.metric.activity.steps import (
    ActivityStepsBulkCreate,
    ActivityStepsBulkCreateResponse,
    ActivityStepsDeleteResponse,
    ActivityStepsExportResponse,
    ActivityStepsResponse,
)
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/steps", tags=["metric-steps"])


@router.get("/", response_model=ActivityStepsExportResponse)
async def get_steps_data(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: AuthUser = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get steps data"""
    try:
        # Only show data for the authenticated user (security)
        query = db.query(ActivitySteps).filter(ActivitySteps.user_id == current_user.id)

        # Apply date filters if provided
        if start_date:
            query = query.filter(ActivitySteps.date_hour >= start_date)
        if end_date:
            query = query.filter(ActivitySteps.date_hour <= end_date)

        # Execute query and convert to list of dictionaries
        records = query.order_by(ActivitySteps.date_hour.desc()).all()
        records_data = [
            {
                "user_id": record.user_id,
                "date_hour": record.date_hour.isoformat(),
                "steps": record.steps,
                "source": record.source,
                "created_at": (
                    record.created_at.isoformat()
                    if record.created_at is not None
                    else None
                ),
                "updated_at": (
                    record.updated_at.isoformat()
                    if record.updated_at is not None
                    else None
                ),
            }
            for record in records
        ]

        # Convert dictionaries to response objects
        response_records = [
            ActivityStepsResponse(**record_data) for record_data in records_data
        ]

        return ActivityStepsExportResponse(
            records=response_records,
            total_count=len(response_records),
            user_id=str(current_user.id),
        )

    except Exception as e:
        logger.error(f"Error retrieving steps data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve steps records",
        )


@router.post("/bulk", response_model=ActivityStepsBulkCreateResponse)
async def create_or_update_multiple_steps_records(
    bulk_data: ActivityStepsBulkCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Create or update multiple steps records (bulk upsert)"""
    try:
        created_count = 0
        updated_count = 0
        processed_records = []

        for steps_data in bulk_data.records:
            # Check if record already exists for this date and source
            existing_record = (
                db.query(ActivitySteps)
                .filter(
                    ActivitySteps.user_id == current_user.id,
                    ActivitySteps.date_hour == steps_data.date_hour,
                    ActivitySteps.source == steps_data.source,
                )
                .one_or_none()
            )

            if existing_record:
                # Update existing record
                setattr(existing_record, "steps", steps_data.steps)
                setattr(existing_record, "updated_at", datetime.utcnow())
                processed_records.append(existing_record)
                updated_count += 1
            else:
                # Create new steps record
                new_record = ActivitySteps(
                    id=generate_rid("metric", "activity_steps"),
                    user_id=current_user.id,
                    date_hour=steps_data.date_hour,
                    steps=steps_data.steps,
                    source=steps_data.source,
                )
                db.add(new_record)
                processed_records.append(new_record)
                created_count += 1

        # Commit all changes at once
        db.commit()

        logger.info(
            f"Bulk processed {len(bulk_data.records)} steps records for {current_user.id}: "
            f"{created_count} created, {updated_count} updated"
        )

        return ActivityStepsBulkCreateResponse(
            message=f"Bulk operation completed: {created_count} created, {updated_count} updated",
            created_count=created_count,
            updated_count=updated_count,
            total_processed=len(bulk_data.records),
            records=processed_records,
        )

    except Exception as e:
        logger.error(f"Error in bulk upsert of steps records: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in bulk upsert: {str(e)}",
        )


@router.get("/{record_id}", response_model=ActivityStepsResponse)
async def get_steps_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Get a specific steps record by ID"""
    try:
        record = (
            db.query(ActivitySteps)
            .filter(
                ActivitySteps.id == record_id,
                ActivitySteps.user_id == current_user.id,
            )
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Steps record not found",
            )

        logger.info(f"Retrieved steps record {record_id} for {current_user.id}")
        return record

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving steps record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving record: {str(e)}",
        )


@router.delete("/{record_id}", response_model=ActivityStepsDeleteResponse)
async def delete_steps_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Delete a steps record"""
    try:
        # Find and delete the record
        record = (
            db.query(ActivitySteps)
            .filter(
                ActivitySteps.id == record_id,
                ActivitySteps.user_id == current_user.id,
            )
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Steps record not found to delete",
            )

        db.delete(record)
        db.commit()

        logger.info(f"Deleted steps record {record_id} for {current_user.id}")
        return ActivityStepsDeleteResponse(
            message="Steps record deleted successfully", deleted_count=1
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting steps record: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting record: {str(e)}",
        )
