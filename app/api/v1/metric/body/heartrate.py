import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.db.session import get_db
from app.models.auth.user import AuthUser
from app.models.metric.body.heartrate import BodyHeartRate
from app.schemas.metric.body.heartrate import (
    HeartRateBulkCreate,
    HeartRateBulkCreateResponse,
    HeartRateDeleteResponse,
    HeartRateExportRecord,
    HeartRateExportResponse,
    HeartRateResponse,
)
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/heartrate", tags=["metric-body-heartrate"])


@router.get("/", response_model=HeartRateExportResponse)
async def get_heart_rate_data(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: AuthUser = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get heart rate data"""
    try:
        # Only show data for the authenticated user (security)
        query = db.query(BodyHeartRate).filter(BodyHeartRate.user_id == current_user.id)

        # Apply date filters if provided
        if start_date:
            query = query.filter(BodyHeartRate.date_hour >= start_date)
        if end_date:
            query = query.filter(BodyHeartRate.date_hour <= end_date)

        # Execute query and convert to list of dictionaries
        records = query.order_by(BodyHeartRate.date_hour.desc()).all()
        records_data = [
            {
                "user_id": record.user_id,
                "date_hour": record.date_hour.isoformat(),
                "heart_rate": record.heart_rate,
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
            HeartRateExportRecord(**record_data) for record_data in records_data
        ]

        return HeartRateExportResponse(
            records=response_records,
            total_count=len(response_records),
            user_id=str(current_user.id),
        )

    except Exception as e:
        logger.error(f"Error retrieving heart rate data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve heart rate records",
        )


@router.post("/bulk", response_model=HeartRateBulkCreateResponse)
async def create_or_update_multiple_heart_rate_records(
    bulk_data: HeartRateBulkCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Create or update multiple heart rate records (bulk upsert)"""
    try:
        created_count = 0
        updated_count = 0
        processed_records = []

        for heart_rate_data in bulk_data.records:
            # Check if record already exists for this date and source
            existing_record = (
                db.query(BodyHeartRate)
                .filter(
                    BodyHeartRate.user_id == current_user.id,
                    BodyHeartRate.date_hour == heart_rate_data.date_hour,
                    BodyHeartRate.source == heart_rate_data.source,
                )
                .one_or_none()
            )

            if existing_record:
                # Update existing record
                if heart_rate_data.heart_rate is not None:
                    setattr(existing_record, "heart_rate", heart_rate_data.heart_rate)
                if heart_rate_data.avg_hr is not None:
                    setattr(existing_record, "avg_hr", heart_rate_data.avg_hr)
                if heart_rate_data.max_hr is not None:
                    setattr(existing_record, "max_hr", heart_rate_data.max_hr)
                if heart_rate_data.min_hr is not None:
                    setattr(existing_record, "min_hr", heart_rate_data.min_hr)
                if heart_rate_data.resting_hr is not None:
                    setattr(existing_record, "resting_hr", heart_rate_data.resting_hr)
                if heart_rate_data.heart_rate_variability is not None:
                    setattr(
                        existing_record,
                        "heart_rate_variability",
                        heart_rate_data.heart_rate_variability,
                    )
                setattr(existing_record, "updated_at", datetime.utcnow())
                processed_records.append(existing_record)
                updated_count += 1
            else:
                # Create new heart rate record
                new_record = BodyHeartRate(
                    id=generate_rid("metric", "body_heartrate"),
                    user_id=current_user.id,
                    date_hour=heart_rate_data.date_hour,
                    heart_rate=heart_rate_data.heart_rate,
                    min_hr=heart_rate_data.min_hr,
                    avg_hr=heart_rate_data.avg_hr,
                    max_hr=heart_rate_data.max_hr,
                    resting_hr=heart_rate_data.resting_hr,
                    heart_rate_variability=heart_rate_data.heart_rate_variability,
                    source=heart_rate_data.source,
                )
                db.add(new_record)
                processed_records.append(new_record)
                created_count += 1

        # Commit all changes at once
        db.commit()

        logger.info(
            f"Bulk processed {len(bulk_data.records)} heart rate records for {current_user.id}: "
            f"{created_count} created, {updated_count} updated"
        )

        return HeartRateBulkCreateResponse(
            message=f"Bulk operation completed: {created_count} created, {updated_count} updated",
            created_count=created_count,
            updated_count=updated_count,
            total_processed=len(bulk_data.records),
            records=processed_records,
        )

    except Exception as e:
        logger.error(f"Error in bulk upsert of heart rate records: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in bulk upsert: {str(e)}",
        )


@router.get("/{record_id}", response_model=HeartRateResponse)
async def get_heart_rate_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Get a specific heart rate record by ID"""
    try:
        record = (
            db.query(BodyHeartRate)
            .filter(
                BodyHeartRate.id == record_id,
                BodyHeartRate.user_id == current_user.id,
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


@router.delete("/{record_id}", response_model=HeartRateDeleteResponse)
async def delete_heart_rate_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Delete a heart rate record"""
    try:
        # Find and delete the record
        record = (
            db.query(BodyHeartRate)
            .filter(
                BodyHeartRate.id == record_id,
                BodyHeartRate.user_id == current_user.id,
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
