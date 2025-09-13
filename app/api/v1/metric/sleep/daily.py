import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.db.session import get_db
from app.models.auth.user import AuthUser
from app.models.metric.sleep.daily import SleepDaily
from app.schemas.metric.sleep.daily import (
    SleepDailyBulkCreate,
    SleepDailyBulkCreateResponse,
    SleepDailyDeleteResponse,
    SleepDailyResponse,
)
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/daily", tags=["daily-sleep"])


@router.get("/", response_model=list[SleepDailyResponse])
async def get_sleep_daily(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Get sleep daily data"""
    try:
        query = db.query(SleepDaily).filter(SleepDaily.user_id == current_user.id)

        # Apply date filters if provided
        if start_date:
            query = query.filter(SleepDaily.date_day >= start_date)
        if end_date:
            query = query.filter(SleepDaily.date_day <= end_date)

        records = query.order_by(SleepDaily.date_day.desc()).all()

        logger.info(
            f"Retrieved {len(records)} sleep daily records for {current_user.id}"
        )
        return records

    except Exception as e:
        logger.error(f"Error retrieving sleep daily: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving data: {str(e)}",
        )


@router.post("/bulk", response_model=SleepDailyBulkCreateResponse)
async def create_or_update_multiple_sleep_records(
    bulk_data: SleepDailyBulkCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Create or update multiple sleep records (bulk upsert)"""
    try:
        created_count = 0
        updated_count = 0
        processed_records = []

        for sleep_data in bulk_data.records:
            # Check if record already exists for this date_day and source
            existing_record = (
                db.query(SleepDaily)
                .filter(
                    SleepDaily.user_id == current_user.id,
                    SleepDaily.date_day == sleep_data.sleep_date,
                    SleepDaily.source == sleep_data.source,
                )
                .one_or_none()
            )

            if existing_record:
                # Update existing record
                if sleep_data.bedtime is not None:
                    setattr(existing_record, "bedtime", sleep_data.bedtime)
                if sleep_data.wake_time is not None:
                    setattr(existing_record, "wake_time", sleep_data.wake_time)
                if sleep_data.total_sleep_minutes is not None:
                    setattr(
                        existing_record,
                        "total_sleep_minutes",
                        sleep_data.total_sleep_minutes,
                    )
                if sleep_data.deep_sleep_minutes is not None:
                    setattr(
                        existing_record,
                        "deep_sleep_minutes",
                        sleep_data.deep_sleep_minutes,
                    )
                if sleep_data.light_sleep_minutes is not None:
                    setattr(
                        existing_record,
                        "light_sleep_minutes",
                        sleep_data.light_sleep_minutes,
                    )
                if sleep_data.rem_sleep_minutes is not None:
                    setattr(
                        existing_record,
                        "rem_sleep_minutes",
                        sleep_data.rem_sleep_minutes,
                    )
                if sleep_data.awake_minutes is not None:
                    setattr(existing_record, "awake_minutes", sleep_data.awake_minutes)
                if sleep_data.sleep_efficiency is not None:
                    setattr(
                        existing_record, "sleep_efficiency", sleep_data.sleep_efficiency
                    )
                if sleep_data.sleep_quality_score is not None:
                    setattr(
                        existing_record,
                        "sleep_quality_score",
                        sleep_data.sleep_quality_score,
                    )
                if sleep_data.notes is not None:
                    setattr(existing_record, "notes", sleep_data.notes)
                setattr(existing_record, "updated_at", datetime.utcnow())
                processed_records.append(existing_record)
                updated_count += 1
            else:
                # Create new sleep record
                new_record = SleepDaily(
                    id=generate_rid("metric", "sleep_daily"),
                    user_id=current_user.id,
                    date_day=sleep_data.sleep_date,
                    bedtime=sleep_data.bedtime,
                    wake_time=sleep_data.wake_time,
                    total_sleep_minutes=sleep_data.total_sleep_minutes,
                    deep_sleep_minutes=sleep_data.deep_sleep_minutes,
                    light_sleep_minutes=sleep_data.light_sleep_minutes,
                    rem_sleep_minutes=sleep_data.rem_sleep_minutes,
                    awake_minutes=sleep_data.awake_minutes,
                    sleep_efficiency=sleep_data.sleep_efficiency,
                    sleep_quality_score=sleep_data.sleep_quality_score,
                    source=sleep_data.source,
                    notes=sleep_data.notes,
                )
                db.add(new_record)
                processed_records.append(new_record)
                created_count += 1

        # Commit all changes at once
        db.commit()

        logger.info(
            f"Bulk processed {len(bulk_data.records)} sleep records for {current_user.id}: "
            f"{created_count} created, {updated_count} updated"
        )

        return SleepDailyBulkCreateResponse(
            message=f"Bulk operation completed: {created_count} created, {updated_count} updated",
            created_count=created_count,
            updated_count=updated_count,
            total_processed=len(bulk_data.records),
            records=processed_records,
        )

    except Exception as e:
        logger.error(f"Error in bulk upsert of sleep records: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in bulk upsert: {str(e)}",
        )


@router.get("/{record_id}", response_model=SleepDailyResponse)
async def get_sleep_daily_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Get a specific sleep daily record by ID"""
    try:
        record = (
            db.query(SleepDaily)
            .filter(
                SleepDaily.id == record_id,
                SleepDaily.user_id == current_user.id,
            )
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sleep daily record not found",
            )

        logger.info(f"Retrieved sleep daily record {record_id} for {current_user.id}")
        return record

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving sleep daily record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving record: {str(e)}",
        )


@router.delete("/{record_id}", response_model=SleepDailyDeleteResponse)
async def delete_sleep_daily_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Delete a sleep daily record"""
    try:
        # Find and delete the record
        record = (
            db.query(SleepDaily)
            .filter(
                SleepDaily.id == record_id,
                SleepDaily.user_id == current_user.id,
            )
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sleep daily record not found to delete",
            )

        db.delete(record)
        db.commit()

        logger.info(f"Deleted sleep daily record {record_id} for {current_user.id}")
        return SleepDailyDeleteResponse(
            message="Sleep daily record deleted successfully", deleted_count=1
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting sleep daily record: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting record: {str(e)}",
        )
