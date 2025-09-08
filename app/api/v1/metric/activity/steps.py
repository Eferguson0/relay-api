import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.db.session import get_db
from app.models.auth.user import User
from app.models.metric.activity.steps import ActivitySteps
from app.schemas.metric.activity.steps import (
    ActivityStepsCreate,
    ActivityStepsCreateResponse,
    ActivityStepsDeleteResponse,
    ActivityStepsExportResponse,
    ActivityStepsIngestRequest,
    ActivityStepsIngestResponse,
    ActivityStepsResponse,
    ActivityStepsUpdate,
    ActivityStepsUpdateResponse,
)
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/metric/steps", tags=["metric-steps"])


@router.get("/")
async def get_steps_data(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get steps data"""
    try:
        # Only show data for the authenticated user (security)
        query = db.query(ActivitySteps).filter(ActivitySteps.user_id == current_user.id)

        # Apply date filters if provided
        if start_date:
            query = query.filter(ActivitySteps.date >= start_date)
        if end_date:
            query = query.filter(ActivitySteps.date <= end_date)

        # Execute query and convert to list of dictionaries
        records = query.order_by(ActivitySteps.date.desc()).all()
        records_data = [
            {
                "user_id": record.user_id,
                "date": record.date.isoformat(),
                "steps": record.steps,
                "source": record.source,
                "created_at": (
                    record.created_at.isoformat() if record.created_at else None
                ),
                "updated_at": (
                    record.updated_at.isoformat() if record.updated_at else None
                ),
            }
            for record in records
        ]

        return ActivityStepsExportResponse(
            records=records_data,
            total_count=len(records_data),
            user_id=current_user.id,
        )

    except Exception as e:
        logger.error(f"Error retrieving steps data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve steps records",
        )


@router.post("/", response_model=ActivityStepsIngestResponse)
async def ingest_steps_data(
    request: ActivityStepsIngestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Ingest steps data from request body and store in hourly_steps table"""
    try:
        # Use the authenticated user
        user = current_user

        # Process the hourly steps data from request body
        records_processed = 0
        metrics_processed = []

        for metric in request.record.data.metrics:
            if metric.name != "hourly_steps":
                continue

            metrics_processed.append(metric.name)

            for data_point in metric.data:
                # Parse the date string
                try:
                    # Handle different date formats
                    date_str = data_point.date
                    if "T" in date_str:
                        # ISO format with time
                        steps_datetime = datetime.fromisoformat(
                            date_str.replace("Z", "+00:00")
                        )
                    else:
                        # Date only format
                        steps_datetime = datetime.fromisoformat(date_str)
                except ValueError as e:
                    logger.warning(f"Invalid date format: {date_str}, error: {e}")
                    continue

                source = data_point.source
                if not source:
                    continue

                # Check if record already exists (upsert behavior)
                existing_record = (
                    db.query(ActivitySteps)
                    .filter(
                        ActivitySteps.user_id == user.id,
                        ActivitySteps.date == steps_datetime,
                        ActivitySteps.source == source,
                    )
                    .first()
                )

                if existing_record:
                    # Update existing record
                    existing_record.steps = data_point.steps
                    existing_record.updated_at = datetime.utcnow()
                else:
                    # Create new record
                    new_record = ActivitySteps(
                        user_id=user.id,
                        date=steps_datetime,
                        steps=data_point.steps,
                        source=source,
                    )
                    db.add(new_record)

                records_processed += 1

        db.commit()

        logger.info(f"Processed {records_processed} steps records for user {user.id}")

        return ActivityStepsIngestResponse(
            message="Steps data ingested successfully",
            records_processed=records_processed,
            metrics_processed=metrics_processed,
            user_id=user.id,
            source="POST request",
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Error ingesting steps data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting data: {str(e)}",
        )


@router.get("/{record_id}", response_model=ActivityStepsResponse)
async def get_hourly_steps_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific hourly steps record by ID"""
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
                detail="Hourly steps record not found",
            )

        logger.info(f"Retrieved hourly steps record {record_id} for {current_user.id}")
        return record

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving hourly steps record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving record: {str(e)}",
        )


@router.post("/record", response_model=ActivityStepsCreateResponse)
async def create_hourly_steps_record(
    steps_data: ActivityStepsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new hourly steps record"""
    try:
        # Check if record already exists for this date and source
        existing_record = (
            db.query(ActivitySteps)
            .filter(
                ActivitySteps.user_id == current_user.id,
                ActivitySteps.date == steps_data.date,
                ActivitySteps.source == steps_data.source,
            )
            .first()
        )

        if existing_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hourly steps record already exists for this date and source. Use PUT to update it.",
            )

        # Create new hourly steps record
        new_record = ActivitySteps(
            id=generate_rid("metric", "hourly_steps"),
            user_id=current_user.id,
            date=steps_data.date,
            steps=steps_data.steps,
            source=steps_data.source,
            notes=steps_data.notes,
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)

        logger.info(f"Created hourly steps record for {current_user.id}")
        return ActivityStepsCreateResponse(
            message="Hourly steps record created successfully", record=new_record
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating hourly steps record: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating record: {str(e)}",
        )


@router.put("/{record_id}", response_model=ActivityStepsUpdateResponse)
async def update_hourly_steps_record(
    record_id: str,
    steps_data: ActivityStepsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an hourly steps record"""
    try:
        # Find existing record
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
                detail="Hourly steps record not found to update",
            )

        # Update fields if provided
        if steps_data.date is not None:
            record.date = steps_data.date
        if steps_data.steps is not None:
            record.steps = steps_data.steps
        if steps_data.source is not None:
            record.source = steps_data.source
        if steps_data.notes is not None:
            record.notes = steps_data.notes

        db.commit()
        db.refresh(record)

        logger.info(f"Updated hourly steps record {record_id} for {current_user.id}")
        return ActivityStepsUpdateResponse(
            message="Hourly steps record updated successfully", record=record
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating hourly steps record: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating record: {str(e)}",
        )


@router.delete("/{record_id}", response_model=ActivityStepsDeleteResponse)
async def delete_hourly_steps_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete an hourly steps record"""
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
                detail="Hourly steps record not found to delete",
            )

        db.delete(record)
        db.commit()

        logger.info(f"Deleted hourly steps record {record_id} for {current_user.id}")
        return ActivityStepsDeleteResponse(
            message="Hourly steps record deleted successfully", deleted_count=1
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting hourly steps record: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting record: {str(e)}",
        )
