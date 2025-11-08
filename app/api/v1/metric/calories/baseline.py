import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.auth.user import AuthUser
from app.schemas.metric.calories.baseline import (
    CaloriesBaselineBulkCreate,
    CaloriesBaselineBulkCreateResponse,
    CaloriesBaselineDeleteResponse,
    CaloriesBaselineResponse,
)
from app.services.auth_service import get_current_active_user
from app.services.metrics_service import MetricsService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/baseline",
    tags=["metric-calories-baseline"],
)


@router.get("/",
    response_model=list[CaloriesBaselineResponse],
    summary="Get calories baseline data endpoint",
    description="Get calories baseline data",
    responses={
        200: {"description": "Calories baseline data retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        500: {"description": "Internal server error"},
    },
)
async def get_calories_baseline(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Get calories baseline data"""
    try:
        metrics_service = MetricsService(db)
        records = metrics_service.get_baseline_calories_data(
            current_user.id, start_date, end_date
        )

        logger.info(
            f"Retrieved {len(records)} calories baseline records for {current_user.id}"
        )
        return [
            CaloriesBaselineResponse.model_validate(record) for record in records
        ]

    except Exception as e:
        logger.error(f"Error retrieving calories baseline: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving data: {str(e)}",
        )


@router.post("/bulk",
    response_model=CaloriesBaselineBulkCreateResponse,
    summary="Create or update multiple baseline calories records (bulk upsert) endpoint",
    description="Create or update multiple baseline calories records (bulk upsert)",
    responses={
        200: {"description": "Baseline calories records created or updated successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        500: {"description": "Internal server error"},
    },
)
async def create_or_update_multiple_baseline_calories_records(
    bulk_data: CaloriesBaselineBulkCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Create or update multiple baseline calories records (bulk upsert)"""
    try:
        metrics_service = MetricsService(db)
        processed_records, created_count, updated_count = (
            metrics_service.create_or_update_multiple_baseline_calories_records(
                bulk_data, current_user.id
            )
        )

        logger.info(
            f"Bulk processed {len(bulk_data.records)} baseline calories records for {current_user.id}: "
            f"{created_count} created, {updated_count} updated"
        )

        return CaloriesBaselineBulkCreateResponse(
            message=f"Bulk operation completed: {created_count} created, {updated_count} updated",
            created_count=created_count,
            updated_count=updated_count,
            total_processed=len(bulk_data.records),
            records=[
                CaloriesBaselineResponse.model_validate(record)
                for record in processed_records
            ],
        )

    except Exception as e:
        logger.error(f"Error in bulk upsert of baseline calories records: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in bulk upsert: {str(e)}",
        )


@router.get("/{record_id}", response_model=CaloriesBaselineResponse,
    summary="Get a specific baseline calories record by ID endpoint",
    description="Get a specific baseline calories record by ID",
    responses={
        200: {"description": "Baseline calories record retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Baseline calories record not found"},
    },
)
async def get_calories_baseline_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Get a specific calories baseline record by ID"""
    try:
        metrics_service = MetricsService(db)
        record = metrics_service.get_baseline_calories_record(
            current_user.id, record_id
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calories baseline record not found",
            )

        logger.info(
            f"Retrieved calories baseline record {record_id} for {current_user.id}"
        )
        return CaloriesBaselineResponse.model_validate(record)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving calories baseline record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving record: {str(e)}",
        )


@router.delete("/{record_id}",
    response_model=CaloriesBaselineDeleteResponse,
    summary="Delete a baseline calories record endpoint",
    description="Delete a baseline calories record",
    responses={
        200: {"description": "Baseline calories record deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Baseline calories record not found to delete"},
    },
)
async def delete_calories_baseline_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Delete a calories baseline record"""
    try:
        metrics_service = MetricsService(db)
        record = metrics_service.delete_baseline_calories_record(
            current_user.id, record_id
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calories baseline record not found to delete",
            )

        logger.info(
            f"Deleted calories baseline record {record_id} for {current_user.id}"
        )
        return CaloriesBaselineDeleteResponse(
            message="Calories baseline record deleted successfully", deleted_count=1
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting calories baseline record: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting record: {str(e)}",
        )
