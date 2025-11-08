import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.auth.user import AuthUser
from app.schemas.metric.sleep.daily import (
    SleepDailyBulkCreate,
    SleepDailyBulkCreateResponse,
    SleepDailyDeleteResponse,
    SleepDailyResponse,
)
from app.services.auth_service import get_current_active_user
from app.services.metrics_service import MetricsService

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
        metrics_service = MetricsService(db)
        records = metrics_service.get_sleep_daily_data(
            current_user.id, start_date, end_date
        )

        logger.info(
            f"Retrieved {len(records)} sleep daily records for {current_user.id}"
        )
        return [SleepDailyResponse.model_validate(record) for record in records]

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
        metrics_service = MetricsService(db)
        processed_records, created_count, updated_count = (
            metrics_service.create_or_update_multiple_sleep_daily_records(
                bulk_data, current_user.id
            )
        )

        logger.info(
            f"Bulk processed {len(bulk_data.records)} sleep records for {current_user.id}: "
            f"{created_count} created, {updated_count} updated"
        )

        return SleepDailyBulkCreateResponse(
            message=f"Bulk operation completed: {created_count} created, {updated_count} updated",
            created_count=created_count,
            updated_count=updated_count,
            total_processed=len(bulk_data.records),
            records=[
                SleepDailyResponse.model_validate(record) for record in processed_records
            ],
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
        metrics_service = MetricsService(db)
        record = metrics_service.get_sleep_daily_record(current_user.id, record_id)

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sleep daily record not found",
            )

        logger.info(f"Retrieved sleep daily record {record_id} for {current_user.id}")
        return SleepDailyResponse.model_validate(record)

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
        metrics_service = MetricsService(db)
        record = metrics_service.delete_sleep_daily_record(current_user.id, record_id)

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sleep daily record not found to delete",
            )

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
