import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.db.session import get_db
from app.models.auth.user import AuthUser
from app.models.metric.activity.miles import ActivityMiles
from app.schemas.metric.activity.miles import (
    ActivityMilesBulkCreate,
    ActivityMilesBulkCreateResponse,
    ActivityMilesDeleteResponse,
    ActivityMilesResponse,
)
from app.services.auth_service import get_current_active_user
from app.services.metrics_service import MetricsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/miles", tags=["metric-miles"])


@router.get("/",
    response_model=list[ActivityMilesResponse],
    summary="Get activity miles data endpoint",
    description="Get activity miles data",
    responses={
        200: {"description": "Activity miles data retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        500: {"description": "Internal server error"},
    }
)
async def get_activity_miles(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Get activity miles data"""
    try:

        metrics_service = MetricsService(db)
        miles_data = metrics_service.get_miles_data(current_user.id, start_date, end_date)

        logger.info(
            f"Retrieved {len(miles_data)} activity miles records for {current_user.id}"
        )
        return miles_data

    except Exception as e:
        logger.error(f"Error retrieving activity miles: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving data: {str(e)}",
        )


@router.get("/{record_id}",
    response_model=ActivityMilesResponse,
    summary="Get a specific activity miles record by ID endpoint",
    description="Get a specific activity miles record by ID",
    responses={
        200: {"description": "Activity miles record retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Activity miles record not found"},
    }
)
async def get_activity_mile_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Get a specific activity miles record by ID"""
    try:

        metrics_service = MetricsService(db)
        miles_data = metrics_service.get_miles_data_by_id(current_user.id, record_id)

        if not miles_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity miles record not found",
            )

        logger.info(
            f"Retrieved activity miles record {record_id} for {current_user.id}"
        )
        return miles_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving activity miles record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving record: {str(e)}",
        )


@router.post("/bulk",
    response_model=ActivityMilesBulkCreateResponse,
    summary="Create or update multiple activity miles records (bulk upsert) endpoint",
    description="Create or update multiple activity miles records (bulk upsert)",
    responses={
        200: {"description": "Activity miles records created or updated successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        500: {"description": "Internal server error"},
    }
)
async def create_or_update_multiple_activity_miles_records(
    bulk_data: ActivityMilesBulkCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Create or update multiple activity miles records (bulk upsert)"""
    try:

        metrics_service = MetricsService(db)
        processed_records, created_count, updated_count = metrics_service.create_or_update_multiple_miles_records(bulk_data, current_user.id)

        return ActivityMilesBulkCreateResponse(
            message=f"Bulk operation completed: {created_count} created, {updated_count} updated",
            created_count=created_count,
            updated_count=updated_count,
            total_processed=len(bulk_data.records),
            records=processed_records,
        )

    except Exception as e:
        logger.error(f"Error in bulk upsert of activity miles records: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in bulk upsert: {str(e)}",
        )


@router.delete("/{record_id}",
    response_model=ActivityMilesDeleteResponse,
    summary="Delete an activity miles record endpoint",
    description="Delete an activity miles record",
    responses={
        200: {"description": "Activity miles record deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Activity miles record not found to delete"},
    }
)
async def delete_activity_miles_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Delete an activity miles record"""
    try:
        
        metrics_service = MetricsService(db)
        record = metrics_service.delete_miles_record(current_user.id, record_id)
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity miles record not found to delete",
            )


        logger.info(f"Deleted activity miles record {record_id} for {current_user.id}")
        return ActivityMilesDeleteResponse(
            message="Activity miles record deleted successfully", deleted_count=1
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting activity miles record: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting record: {str(e)}",
        )
