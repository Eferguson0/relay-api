import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.auth.user import AuthUser
from app.schemas.metric.body.heartrate import (
    HeartRateBulkCreate,
    HeartRateBulkCreateResponse,
    HeartRateDeleteResponse,
    HeartRateExportRecord,
    HeartRateExportResponse,
    HeartRateResponse,
)
from app.services.auth_service import get_current_active_user
from app.services.metrics_service import MetricsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/heartrate", tags=["metric-body-heartrate"])


@router.get("/",
    response_model=HeartRateExportResponse,
    summary="Get heart rate data endpoint",
    description="Get heart rate data",
    responses={
        200: {"description": "Heart rate data retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        500: {"description": "Internal server error"},
    },
)
async def get_heart_rate_data(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: AuthUser = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get heart rate data"""
    try:
        metrics_service = MetricsService(db)
        records = metrics_service.get_heart_rate_data(current_user.id, start_date, end_date)

        response_records = [
            HeartRateExportRecord.model_validate(record, from_attributes=True)
            for record in records
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


@router.post("/bulk",
    response_model=HeartRateBulkCreateResponse,
    summary="Create or update multiple heart rate records (bulk upsert) endpoint",
    description="Create or update multiple heart rate records (bulk upsert)",
    responses={
        200: {"description": "Heart rate records created or updated successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        500: {"description": "Internal server error"},
    },
)
async def create_or_update_multiple_heart_rate_records(
    bulk_data: HeartRateBulkCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Create or update multiple heart rate records (bulk upsert)"""
    try:
        metrics_service = MetricsService(db)
        processed_records, created_count, updated_count = (
            metrics_service.create_or_update_multiple_heart_rate_records(
                bulk_data, current_user.id
            )
        )

        logger.info(
            f"Bulk processed {len(bulk_data.records)} heart rate records for {current_user.id}: "
            f"{created_count} created, {updated_count} updated"
        )

        return HeartRateBulkCreateResponse(
            message=f"Bulk operation completed: {created_count} created, {updated_count} updated",
            created_count=created_count,
            updated_count=updated_count,
            total_processed=len(bulk_data.records),
            records=[
                HeartRateResponse.model_validate(record)
                for record in processed_records
            ],
        )

    except Exception as e:
        logger.error(f"Error in bulk upsert of heart rate records: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in bulk upsert: {str(e)}",
        )


@router.get("/{record_id}",
    response_model=HeartRateResponse,
    summary="Get a specific heart rate record by ID endpoint",
    description="Get a specific heart rate record by ID",
    responses={
        200: {"description": "Heart rate record retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Heart rate record not found"},
    },
)
async def get_heart_rate_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Get a specific heart rate record by ID"""
    try:
        metrics_service = MetricsService(db)
        record = metrics_service.get_heart_rate_record(current_user.id, record_id)

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Heart rate record not found",
            )

        logger.info(f"Retrieved heart rate record {record_id} for {current_user.id}")
        return HeartRateResponse.model_validate(record)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving heart rate record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving record: {str(e)}",
        )


@router.delete("/{record_id}",
    response_model=HeartRateDeleteResponse,
    summary="Delete a heart rate record endpoint",
    description="Delete a heart rate record",
    responses={
        200: {"description": "Heart rate record deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Heart rate record not found to delete"},
    },
)
async def delete_heart_rate_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Delete a heart rate record"""
    try:
        metrics_service = MetricsService(db)
        record = metrics_service.delete_heart_rate_record(current_user.id, record_id)

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Heart rate record not found to delete",
            )

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
