import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.db.session import get_db
from app.models.auth.user import User
from app.models.metric.calories.active import CaloriesActive
from app.schemas.metric.calories.active_burn import (
    CaloriesActiveCreate,
    CaloriesActiveCreateResponse,
    CaloriesActiveDeleteResponse,
    CaloriesActiveExportResponse,
    CaloriesActiveIngestRequest,
    CaloriesActiveIngestResponse,
    CaloriesActiveResponse,
    CaloriesActiveUpdate,
    CaloriesActiveUpdateResponse,
)
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/metric/calories/active", tags=["metric-calories-active"]
)


@router.get("/")
async def get_active_calories_burn(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get active calories burn data"""
    try:
        # Only show data for the authenticated user (security)
        query = db.query(CaloriesActive).filter(
            CaloriesActive.user_id == current_user.id
        )

        # Apply date filters if provided
        if start_date:
            query = query.filter(CaloriesActive.date >= start_date)
        if end_date:
            query = query.filter(CaloriesActive.date <= end_date)

        # Execute query and convert to list of dictionaries
        records = query.order_by(CaloriesActive.date.desc()).all()
        records_data = [
            {
                "user_id": record.user_id,
                "date": record.date.isoformat(),
                "calories_burned": (
                    float(record.calories_burned) if record.calories_burned else None
                ),
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

        return CaloriesActiveExportResponse(
            records=records_data,
            total_count=len(records_data),
            user_id=current_user.id,
        )

    except Exception as e:
        logger.error(f"Error retrieving active calories data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve active calories records",
        )


@router.post("/", response_model=CaloriesActiveIngestResponse)
async def ingest_active_calories_burn(
    request: CaloriesActiveIngestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Ingest active calories data from request body and store in active_calories table"""
    try:
        # Use the authenticated user
        user = current_user

        # Process the active calories data from request body
        records_processed = 0
        metrics_processed = []

        for metric in request.record.data.metrics:
            if metric.name != "active_calories":
                continue

            metrics_processed.append(metric.name)

            for data_point in metric.data:
                # Parse the date string
                try:
                    # Handle different date formats
                    date_str = data_point.date
                    if "T" in date_str:
                        # ISO format with time
                        calories_datetime = datetime.fromisoformat(
                            date_str.replace("Z", "+00:00")
                        )
                    else:
                        # Date only format
                        calories_datetime = datetime.fromisoformat(date_str)
                except ValueError as e:
                    logger.warning(f"Invalid date format: {date_str}, error: {e}")
                    continue

                source = data_point.source
                if not source:
                    continue

                # Check if record already exists (upsert behavior)
                existing_record = (
                    db.query(CaloriesActive)
                    .filter(
                        CaloriesActive.user_id == user.id,
                        CaloriesActive.date == calories_datetime,
                        CaloriesActive.source == source,
                    )
                    .first()
                )

                if existing_record:
                    # Update existing record
                    existing_record.calories_burned = data_point.calories_burned
                    existing_record.updated_at = datetime.utcnow()
                else:
                    # Create new record
                    new_record = CaloriesActive(
                        user_id=user.id,
                        date=calories_datetime,
                        calories_burned=data_point.calories_burned,
                        source=source,
                    )
                    db.add(new_record)

                records_processed += 1

        db.commit()

        logger.info(
            f"Processed {records_processed} active calories records for user {user.id}"
        )

        return CaloriesActiveIngestResponse(
            message="Active calories data ingested successfully",
            records_processed=records_processed,
            metrics_processed=metrics_processed,
            user_id=user.id,
            source="POST request",
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Error ingesting active calories data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting data: {str(e)}",
        )


@router.get("/{record_id}", response_model=CaloriesActiveResponse)
async def get_active_calories_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific active calories record by ID"""
    try:
        record = (
            db.query(CaloriesActive)
            .filter(
                CaloriesActive.id == record_id,
                CaloriesActive.user_id == current_user.id,
            )
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active calories record not found",
            )

        logger.info(
            f"Retrieved active calories record {record_id} for {current_user.id}"
        )
        return record

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving active calories record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving record: {str(e)}",
        )


@router.post("/record", response_model=CaloriesActiveCreateResponse)
async def create_active_calories_record(
    calories_data: CaloriesActiveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new active calories record"""
    try:
        # Check if record already exists for this date and source
        existing_record = (
            db.query(CaloriesActive)
            .filter(
                CaloriesActive.user_id == current_user.id,
                CaloriesActive.date == calories_data.date,
                CaloriesActive.source == calories_data.source,
            )
            .first()
        )

        if existing_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Active calories record already exists for this date and source. Use PUT to update it.",
            )

        # Create new active calories record
        new_record = CaloriesActive(
            id=generate_rid("metric", "active_calories"),
            user_id=current_user.id,
            date=calories_data.date,
            calories_burned=calories_data.calories_burned,
            source=calories_data.source,
            notes=calories_data.notes,
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)

        logger.info(f"Created active calories record for {current_user.id}")
        return CaloriesActiveCreateResponse(
            message="Active calories record created successfully", record=new_record
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating active calories record: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating record: {str(e)}",
        )


@router.put("/{record_id}", response_model=CaloriesActiveUpdateResponse)
async def update_active_calories_record(
    record_id: str,
    calories_data: CaloriesActiveUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an active calories record"""
    try:
        # Find existing record
        record = (
            db.query(CaloriesActive)
            .filter(
                CaloriesActive.id == record_id,
                CaloriesActive.user_id == current_user.id,
            )
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active calories record not found to update",
            )

        # Update fields if provided
        if calories_data.date is not None:
            record.date = calories_data.date
        if calories_data.calories_burned is not None:
            record.calories_burned = calories_data.calories_burned
        if calories_data.source is not None:
            record.source = calories_data.source
        if calories_data.notes is not None:
            record.notes = calories_data.notes

        db.commit()
        db.refresh(record)

        logger.info(f"Updated active calories record {record_id} for {current_user.id}")
        return CaloriesActiveUpdateResponse(
            message="Active calories record updated successfully", record=record
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating active calories record: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating record: {str(e)}",
        )


@router.delete("/{record_id}", response_model=CaloriesActiveDeleteResponse)
async def delete_active_calories_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete an active calories record"""
    try:
        # Find and delete the record
        record = (
            db.query(CaloriesActive)
            .filter(
                CaloriesActive.id == record_id,
                CaloriesActive.user_id == current_user.id,
            )
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active calories record not found to delete",
            )

        db.delete(record)
        db.commit()

        logger.info(f"Deleted active calories record {record_id} for {current_user.id}")
        return CaloriesActiveDeleteResponse(
            message="Active calories record deleted successfully", deleted_count=1
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting active calories record: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting record: {str(e)}",
        )
