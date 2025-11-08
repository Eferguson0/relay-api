import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.auth.user import AuthUser
from app.schemas.metric.calories.active import (
    ActiveCaloriesExportRecord,
    ActiveCaloriesExportResponse,
    CaloriesActiveBulkCreate,
    CaloriesActiveBulkCreateResponse,
    CaloriesActiveDeleteResponse,
    CaloriesActiveResponse,
)
from app.services.auth_service import get_current_active_user
from app.services.metrics_service import MetricsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/active", tags=["metric-calories-active"])


@router.get("/",
    response_model=ActiveCaloriesExportResponse,
    summary="Get active calories burn data endpoint",
    description="Get active calories burn data",
    responses={
        200: {"description": "Active calories burn data retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        500: {"description": "Internal server error"},
    },
)
async def get_active_calories_burn(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: AuthUser = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get active calories burn data"""
    try:
        metrics_service = MetricsService(db)
        records = metrics_service.get_active_calories_data(
            current_user.id, start_date, end_date
        )
        response_records = [
            ActiveCaloriesExportRecord(
                id=record.id,
                user_id=record.user_id,
                date_hour=record.date_hour.isoformat(),
                calories_burned=float(record.calories_burned)
                if record.calories_burned is not None
                else None,
                source=getattr(record.source, "value", record.source),
                created_at=record.created_at.isoformat()
                if record.created_at is not None
                else None,
                updated_at=record.updated_at.isoformat()
                if record.updated_at is not None
                else None,
            )
            for record in records
        ]

        return ActiveCaloriesExportResponse(
            records=response_records,
            total_count=len(response_records),
            user_id=str(current_user.id),
        )

    except Exception as e:
        logger.error(f"Error retrieving active calories data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve active calories records",
        )


@router.post("/bulk",
    response_model=CaloriesActiveBulkCreateResponse,
    summary="Create or update multiple active calories records (bulk upsert) endpoint",
    description="Create or update multiple active calories records (bulk upsert)",
    responses={
        200: {"description": "Active calories records created or updated successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        500: {"description": "Internal server error"},
    },
)
async def create_or_update_multiple_active_calories_records(
    bulk_data: CaloriesActiveBulkCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Create or update multiple active calories records (bulk upsert)"""
    try:
        metrics_service = MetricsService(db)
        processed_records, created_count, updated_count = (
            metrics_service.create_or_update_multiple_active_calories_records(
                bulk_data, current_user.id
            )
        )

        logger.info(
            f"Bulk processed {len(bulk_data.records)} active calories records for {current_user.id}: "
            f"{created_count} created, {updated_count} updated"
        )

        return CaloriesActiveBulkCreateResponse(
            message=f"Bulk operation completed: {created_count} created, {updated_count} updated",
            created_count=created_count,
            updated_count=updated_count,
            total_processed=len(bulk_data.records),
            records=[
                CaloriesActiveResponse.model_validate(record)
                for record in processed_records
            ],
        )

    except Exception as e:
        logger.error(f"Error in bulk upsert of active calories records: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in bulk upsert: {str(e)}",
        )


@router.get("/{record_id}",
    response_model=CaloriesActiveResponse,
    summary="Get a specific active calories record by ID endpoint",
    description="Get a specific active calories record by ID",
    responses={
        200: {"description": "Active calories record retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Active calories record not found"},
    },
)
async def get_active_calories_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Get a specific active calories record by ID"""
    try:
        metrics_service = MetricsService(db)
        record = metrics_service.get_active_calories_record(
            current_user.id, record_id
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active calories record not found",
            )

        logger.info(
            f"Retrieved active calories record {record_id} for {current_user.id}"
        )
        return CaloriesActiveResponse.model_validate(record)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving active calories record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving record: {str(e)}",
        )


@router.delete("/{record_id}",
    response_model=CaloriesActiveDeleteResponse,
    summary="Delete an active calories record endpoint",
    description="Delete an active calories record",
    responses={
        200: {"description": "Active calories record deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Active calories record not found to delete"},
    },
)
async def delete_active_calories_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Delete an active calories record"""
    try:
        metrics_service = MetricsService(db)
        record = metrics_service.delete_active_calories_record(
            current_user.id, record_id
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active calories record not found to delete",
            )

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
