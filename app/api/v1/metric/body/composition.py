import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.auth.user import AuthUser
from app.schemas.metric.body.composition import (
    BodyCompositionBulkCreate,
    BodyCompositionBulkCreateResponse,
    BodyCompositionDeleteResponse,
    BodyCompositionExportResponse,
    BodyCompositionResponse,
)
from app.services.auth_service import get_current_active_user
from app.services.metrics_service import MetricsService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/composition", tags=["metric-body-composition"])


@router.get("/",
    response_model=BodyCompositionExportResponse,
    summary="Get body composition data endpoint",
    description="Get body composition data (weight, body fat, muscle mass)",
    responses={
    200: {"description": "Body composition data retrieved successfully"},
    401: {"description": "Unauthorized"},
    403: {"description": "Inactive user"},
    500: {"description": "Internal server error"},
    },
)
async def get_body_composition(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: AuthUser = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get body composition data (weight, body fat, muscle mass)"""
    try:
        metrics_service = MetricsService(db)
        records = metrics_service.get_body_composition_data(current_user.id, start_date, end_date)

        records_data = [
            BodyCompositionResponse.model_validate(record) for record in records
        ]

        return BodyCompositionExportResponse(
            records=records_data,
            total_count=len(records_data),
            user_id=str(current_user.id),
        )

    except Exception as e:
        logger.error(f"Error fetching body composition records: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching data: {str(e)}",
        )


@router.post("/bulk",
    response_model=BodyCompositionBulkCreateResponse,
    summary="Create or update multiple body composition records (bulk upsert) endpoint",
    description="Create or update multiple body composition records (bulk upsert)",
    responses={
        200: {"description": "Body composition records created or updated successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        500: {"description": "Internal server error"},
    },
)
async def create_or_update_multiple_body_composition_records(
    bulk_data: BodyCompositionBulkCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Create or update multiple body composition records (bulk upsert)"""
    try:
        metrics_service = MetricsService(db)
        processed_records, created_count, updated_count = (
            metrics_service.create_or_update_multiple_body_composition_records(
                bulk_data, current_user.id
            )
        )
        logger.info(
            f"Bulk processed {len(bulk_data.records)} body composition records for {current_user.id}: "
            f"{created_count} created, {updated_count} updated"
        )

        return BodyCompositionBulkCreateResponse(
            message=f"Bulk operation completed: {created_count} created, {updated_count} updated",
            created_count=created_count,
            updated_count=updated_count,
            total_processed=len(bulk_data.records),
            records=[
                BodyCompositionResponse.model_validate(record)
                for record in processed_records
            ],
        )

    except Exception as e:
        logger.error(f"Error in bulk upsert of body composition records: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in bulk upsert: {str(e)}",
        )


@router.delete("/{weight_id}",
    response_model=BodyCompositionDeleteResponse,
    summary="Delete a body composition record endpoint",
    description="Delete a body composition record",
    responses={
        200: {"description": "Body composition record deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        500: {"description": "Internal server error"},
    },
)
async def delete_body_composition_record(
    weight_id: str,
    current_user: AuthUser = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a body composition measurement record"""
    try:
        metrics_service = MetricsService(db)
        weight_record = metrics_service.delete_body_composition_record(
            current_user.id, weight_id
        )

        if not weight_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="BodyComposition record not found or you don't have permission to delete it",
            )

        logger.info(
            f"Deleted body composition record {weight_id} for user {current_user.id}"
        )
        return BodyCompositionDeleteResponse(
            message="Body composition record deleted successfully", deleted_count=1
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting body composition record: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete body composition record",
        )
