import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.db.session import get_db
from app.models.auth.user import User
from app.models.metric.body.heartrate import HeartRate
from app.schemas.metric.body.heartrate import (
    HeartRateCreate,
    HeartRateCreateResponse,
    HeartRateDeleteResponse,
    HeartRateIngestRequest,
    HeartRateIngestResponse,
    HeartRateResponse,
    HeartRateUpdate,
    HeartRateUpdateResponse,
)
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/metric/body/heartrate", tags=["metric-body-heartrate"]
)


@router.get("/")
async def get_heart_rate_data(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get heart rate data"""
    try:
        # Only show data for the authenticated user (security)
        query = db.query(HeartRate).filter(HeartRate.user_id == current_user.id)

        # Apply date filters if provided
        if start_date:
            query = query.filter(HeartRate.date >= start_date)
        if end_date:
            query = query.filter(HeartRate.date <= end_date)

        # Execute query and convert to list of dictionaries
        records = query.order_by(HeartRate.date.desc()).all()
        records_data = [
            {
                "user_id": record.user_id,
                "date": record.date.isoformat(),
                "heart_rate": record.heart_rate,
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

        return {
            "records": records_data,
            "total_count": len(records_data),
            "user_id": current_user.id,
        }

    except Exception as e:
        logger.error(f"Error retrieving heart rate data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve heart rate records",
        )


@router.post("/", response_model=HeartRateIngestResponse)
async def ingest_heart_rate_data(
    request: HeartRateIngestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Ingest heart rate data from request body and store in hourly_heart_rate table"""
    try:
        # Use the authenticated user
        user = current_user

        # Process the heart rate data from request body
        records_processed = 0
        metrics_processed = []

        for metric in request.record.data.metrics:
            if metric.name != "heart_rate":
                continue

            metrics_processed.append(metric.name)

            for data_point in metric.data:
                # Parse the date string
                try:
                    # Handle different date formats
                    date_str = data_point.date
                    if "T" in date_str:
                        # ISO format with time
                        heart_rate_datetime = datetime.fromisoformat(
                            date_str.replace("Z", "+00:00")
                        )
                    else:
                        # Date only format
                        heart_rate_datetime = datetime.fromisoformat(date_str)
                except ValueError as e:
                    logger.warning(f"Invalid date format: {date_str}, error: {e}")
                    continue

                source = data_point.source
                if not source:
                    continue

                # Check if record already exists (upsert behavior)
                existing_record = (
                    db.query(HeartRate)
                    .filter(
                        HeartRate.user_id == user.id,
                        HeartRate.date == heart_rate_datetime,
                        HeartRate.source == source,
                    )
                    .first()
                )

                if existing_record:
                    # Update existing record
                    existing_record.heart_rate = data_point.heart_rate
                    existing_record.updated_at = datetime.utcnow()
                else:
                    # Create new record
                    new_record = HeartRate(
                        user_id=user.id,
                        date=heart_rate_datetime,
                        heart_rate=data_point.heart_rate,
                        source=source,
                    )
                    db.add(new_record)

                records_processed += 1

        db.commit()

        logger.info(
            f"Processed {records_processed} heart rate records for user {user.id}"
        )

        return HeartRateIngestResponse(
            message="Heart rate data ingested successfully",
            records_processed=records_processed,
            metrics_processed=metrics_processed,
            user_id=user.id,
            source="POST request",
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Error ingesting heart rate data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting data: {str(e)}",
        )


@router.get("/{record_id}", response_model=HeartRateResponse)
async def get_heart_rate_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific heart rate record by ID"""
    try:
        record = (
            db.query(HeartRate)
            .filter(
                HeartRate.id == record_id,
                HeartRate.user_id == current_user.id,
            )
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Heart rate record not found",
            )

        logger.info(f"Retrieved heart rate record {record_id} for {current_user.id}")
        return record

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving heart rate record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving record: {str(e)}",
        )


@router.post("/record", response_model=HeartRateCreateResponse)
async def create_heart_rate_record(
    heart_rate_data: HeartRateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new heart rate record"""
    try:
        # Check if record already exists for this date and source
        existing_record = (
            db.query(HeartRate)
            .filter(
                HeartRate.user_id == current_user.id,
                HeartRate.date == heart_rate_data.date,
                HeartRate.source == heart_rate_data.source,
            )
            .first()
        )

        if existing_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Heart rate record already exists for this date and source. Use PUT to update it.",
            )

        # Create new heart rate record
        new_record = HeartRate(
            id=generate_rid("metric", "heart_rate"),
            user_id=current_user.id,
            date=heart_rate_data.date,
            heart_rate=heart_rate_data.heart_rate,
            avg_hr=heart_rate_data.avg_hr,
            max_hr=heart_rate_data.max_hr,
            min_hr=heart_rate_data.min_hr,
            resting_hr=heart_rate_data.resting_hr,
            heart_rate_variability=heart_rate_data.heart_rate_variability,
            source=heart_rate_data.source,
            notes=heart_rate_data.notes,
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)

        logger.info(f"Created heart rate record for {current_user.id}")
        return HeartRateCreateResponse(
            message="Heart rate record created successfully", record=new_record
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating heart rate record: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating record: {str(e)}",
        )


@router.put("/{record_id}", response_model=HeartRateUpdateResponse)
async def update_heart_rate_record(
    record_id: str,
    heart_rate_data: HeartRateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a heart rate record"""
    try:
        # Find existing record
        record = (
            db.query(HeartRate)
            .filter(
                HeartRate.id == record_id,
                HeartRate.user_id == current_user.id,
            )
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Heart rate record not found to update",
            )

        # Update fields if provided
        if heart_rate_data.date is not None:
            record.date = heart_rate_data.date
        if heart_rate_data.heart_rate is not None:
            record.heart_rate = heart_rate_data.heart_rate
        if heart_rate_data.avg_hr is not None:
            record.avg_hr = heart_rate_data.avg_hr
        if heart_rate_data.max_hr is not None:
            record.max_hr = heart_rate_data.max_hr
        if heart_rate_data.min_hr is not None:
            record.min_hr = heart_rate_data.min_hr
        if heart_rate_data.resting_hr is not None:
            record.resting_hr = heart_rate_data.resting_hr
        if heart_rate_data.heart_rate_variability is not None:
            record.heart_rate_variability = heart_rate_data.heart_rate_variability
        if heart_rate_data.source is not None:
            record.source = heart_rate_data.source
        if heart_rate_data.notes is not None:
            record.notes = heart_rate_data.notes

        db.commit()
        db.refresh(record)

        logger.info(f"Updated heart rate record {record_id} for {current_user.id}")
        return HeartRateUpdateResponse(
            message="Heart rate record updated successfully", record=record
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating heart rate record: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating record: {str(e)}",
        )


@router.delete("/{record_id}", response_model=HeartRateDeleteResponse)
async def delete_heart_rate_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a heart rate record"""
    try:
        # Find and delete the record
        record = (
            db.query(HeartRate)
            .filter(
                HeartRate.id == record_id,
                HeartRate.user_id == current_user.id,
            )
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Heart rate record not found to delete",
            )

        db.delete(record)
        db.commit()

        logger.info(f"Deleted heart rate record {record_id} for {current_user.id}")
        return HeartRateDeleteResponse(
            message="Heart rate record deleted successfully", deleted_count=1
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting heart rate record: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting record: {str(e)}",
        )
