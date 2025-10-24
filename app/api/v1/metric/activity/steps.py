import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.db.session import get_db
from app.models.auth.user import AuthUser
from app.models.metric.activity.steps import ActivitySteps
from app.schemas.metric.activity.steps import (
    ActivityStepsBulkCreate,
    ActivityStepsBulkCreateResponse,
    ActivityStepsDeleteResponse,
    ActivityStepsExportResponse,
    ActivityStepsResponse,
)
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/steps", tags=["metric-steps"])


@router.get("/",
    response_model=ActivityStepsExportResponse,
    summary="Get steps data endpoint",
    description="Get steps data",
    responses={
        200: {"description": "Steps data retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Steps data not found"},
        500: {"description": "Internal server error"},
    }
)
async def get_steps_data(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: AuthUser = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get steps data"""
    try:
        
        metrics_service = MetricsService(db)
        steps_data = metrics_service.get_steps_data(current_user.id, start_date, end_date)


        if not steps_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Steps data not found",
            )

        logger.info(
            f"Retrieved {len(steps_data)} steps records for {current_user.id}"
        )
        
        return ActivityStepsExportResponse(
            records=[ActivityStepsResponse.model_validate(record) for record in steps_data],
            total_count=len(steps_data),
            user_id=str(current_user.id),
        )


    except Exception as e:
        logger.error(f"Error retrieving steps data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve steps records",
        )


@router.post("/bulk",
    response_model=ActivityStepsBulkCreateResponse,
    summary="Create or update multiple steps records (bulk upsert) endpoint",
    description="Create or update multiple steps records (bulk upsert)",
    responses={
        200: {"description": "Steps records created or updated successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        500: {"description": "Internal server error"},
    }
)
async def create_or_update_multiple_steps_records(
    bulk_data: ActivityStepsBulkCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Create or update multiple steps records (bulk upsert)"""
    try:
        

        metrics_service = MetricsService(db)
        processed_records, created_count, updated_count = metrics_service.create_or_update_multiple_steps_records(bulk_data, current_user.id)

        if not processed_records:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Steps records not found",
            )

        logger.info(
            f"Bulk processed {len(bulk_data.records)} steps records for {current_user.id}: "
            f"{created_count} created, {updated_count} updated"
        )

        return ActivityStepsBulkCreateResponse(
            message=f"Bulk operation completed: {created_count} created, {updated_count} updated",
            created_count=created_count,
            updated_count=updated_count,
            total_processed=len(bulk_data.records),
            records=processed_records,
        )

    except Exception as e:
        logger.error(f"Error in bulk upsert of steps records: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in bulk upsert: {str(e)}",
        )


@router.get("/{record_id}",
    response_model=ActivityStepsResponse,
    summary="Get a specific steps record by ID endpoint",
    description="Get a specific steps record by ID",
    responses={
        200: {"description": "Steps record retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
    }
)
async def get_steps_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Get a specific steps record by ID"""
    try:

        metrics_service = MetricsService(db)
        record = metrics_service.get_steps_data_by_id(current_user.id, record_id)

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Steps record not found",
            )

        logger.info(f"Retrieved steps record {record_id} for {current_user.id}")
        return record

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving steps record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving record: {str(e)}",
        )


@router.delete("/{record_id}",
    response_model=ActivityStepsDeleteResponse,
    summary="Delete a steps record by ID endpoint",
    description="Delete a steps record by ID",
    responses={
        200: {"description": "Steps record deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Steps record not found to delete"},
        500: {"description": "Internal server error"},
    },
)
async def delete_steps_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Delete a steps record"""
    try:
        
        metrics_service = MetricsService(db)
        record = metrics_service.delete_steps_record(current_user.id, record_id)

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Steps record not found to delete",
            )

        logger.info(f"Deleted steps record {record_id} for {current_user.id}")
        return ActivityStepsDeleteResponse(
            message="Steps record deleted successfully", deleted_count=1
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting steps record: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting record: {str(e)}",
        )
