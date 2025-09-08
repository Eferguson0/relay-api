import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.db.session import get_db
from app.models.auth.user import User
from app.models.metric.sleep.daily import SleepDaily
from app.schemas.metric.sleep.daily import (
    SleepDailyCreate,
    SleepDailyCreateResponse,
    SleepDailyDeleteResponse,
    SleepDailyResponse,
    SleepDailyUpdate,
    SleepDailyUpdateResponse,
)
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/metric/sleep", tags=["metric-sleep"])


@router.get("/", response_model=list[SleepDailyResponse])
async def get_sleep_daily(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get sleep daily data"""
    try:
        query = db.query(SleepDaily).filter(SleepDaily.user_id == current_user.id)

        # Apply date filters if provided
        if start_date:
            query = query.filter(SleepDaily.sleep_date >= start_date)
        if end_date:
            query = query.filter(SleepDaily.sleep_date <= end_date)

        records = query.order_by(SleepDaily.sleep_date.desc()).all()

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


@router.get("/{record_id}", response_model=SleepDailyResponse)
async def get_sleep_daily_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
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


@router.post("/", response_model=SleepDailyCreateResponse)
async def create_sleep_daily_record(
    sleep_data: SleepDailyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new sleep daily record"""
    try:
        # Check if record already exists for this sleep_date and source
        existing_record = (
            db.query(SleepDaily)
            .filter(
                SleepDaily.user_id == current_user.id,
                SleepDaily.sleep_date == sleep_data.sleep_date,
                SleepDaily.source == sleep_data.source,
            )
            .first()
        )

        if existing_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sleep daily record already exists for this date and source. Use PUT to update it.",
            )

        # Create new sleep daily record
        new_record = SleepDaily(
            id=generate_rid("metric", "sleep_daily"),
            user_id=current_user.id,
            sleep_date=sleep_data.sleep_date,
            bedtime=sleep_data.bedtime,
            wake_time=sleep_data.wake_time,
            total_sleep_hours=sleep_data.total_sleep_hours,
            deep_sleep_hours=sleep_data.deep_sleep_hours,
            light_sleep_hours=sleep_data.light_sleep_hours,
            rem_sleep_hours=sleep_data.rem_sleep_hours,
            sleep_efficiency=sleep_data.sleep_efficiency,
            source=sleep_data.source,
            notes=sleep_data.notes,
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)

        logger.info(f"Created sleep daily record for {current_user.id}")
        return SleepDailyCreateResponse(
            message="Sleep daily record created successfully", record=new_record
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating sleep daily record: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating record: {str(e)}",
        )


@router.put("/{record_id}", response_model=SleepDailyUpdateResponse)
async def update_sleep_daily_record(
    record_id: str,
    sleep_data: SleepDailyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a sleep daily record"""
    try:
        # Find existing record
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
                detail="Sleep daily record not found to update",
            )

        # Update fields if provided
        if sleep_data.sleep_date is not None:
            record.sleep_date = sleep_data.sleep_date
        if sleep_data.bedtime is not None:
            record.bedtime = sleep_data.bedtime
        if sleep_data.wake_time is not None:
            record.wake_time = sleep_data.wake_time
        if sleep_data.total_sleep_hours is not None:
            record.total_sleep_hours = sleep_data.total_sleep_hours
        if sleep_data.deep_sleep_hours is not None:
            record.deep_sleep_hours = sleep_data.deep_sleep_hours
        if sleep_data.light_sleep_hours is not None:
            record.light_sleep_hours = sleep_data.light_sleep_hours
        if sleep_data.rem_sleep_hours is not None:
            record.rem_sleep_hours = sleep_data.rem_sleep_hours
        if sleep_data.sleep_efficiency is not None:
            record.sleep_efficiency = sleep_data.sleep_efficiency
        if sleep_data.source is not None:
            record.source = sleep_data.source
        if sleep_data.notes is not None:
            record.notes = sleep_data.notes

        db.commit()
        db.refresh(record)

        logger.info(f"Updated sleep daily record {record_id} for {current_user.id}")
        return SleepDailyUpdateResponse(
            message="Sleep daily record updated successfully", record=record
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating sleep daily record: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating record: {str(e)}",
        )


@router.delete("/{record_id}", response_model=SleepDailyDeleteResponse)
async def delete_sleep_daily_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
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
