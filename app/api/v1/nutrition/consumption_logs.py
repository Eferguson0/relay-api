import logging
import traceback
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.datetime_utils import parse_iso_datetime
from app.db.session import get_db
from app.models.auth.user import AuthUser
from app.schemas.nutrition.consumption_logs import (
    ConsumptionLogCreate,
    ConsumptionLogCreateResponse,
    ConsumptionLogDeleteResponse,
    ConsumptionLogListResponse,
    ConsumptionLogResponse,
    ConsumptionLogUpdate,
)
from app.services.auth_service import get_current_active_user
from app.services.nutrition_service import NutritionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/consumption-logs", tags=["nutrition-consumption-logs"])


@router.get(
    "/",
    response_model=ConsumptionLogListResponse,
    summary="List consumption logs",
    description="Retrieve consumption logs for the current user",
    responses={
        200: {"description": "Consumption logs retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        500: {"description": "Internal server error"},
    },
)
async def list_consumption_logs(
    start_date: Optional[str] = Query(
        default=None, description="Filter logs on or after this ISO datetime"
    ),
    end_date: Optional[str] = Query(
        default=None, description="Filter logs on or before this ISO datetime"
    ),
    limit: int = Query(
        default=50, ge=1, le=100, description="Maximum number of logs to return (default: 50, max: 100)"
    ),
    offset: int = Query(
        default=0, ge=0, description="Number of logs to skip (default: 0)"
    ),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
) -> ConsumptionLogListResponse:
    """Return the user's consumption logs with optional date filters."""
    try:
        nutrition_service = NutritionService(db)

        parsed_start = parse_iso_datetime(start_date) if start_date else None
        parsed_end = parse_iso_datetime(end_date) if end_date else None

        logs, total_count = nutrition_service.list_consumption_logs(
            user_id=current_user.id,
            start_date=parsed_start,
            end_date=parsed_end,
            limit=limit,
            offset=offset,
        )

        return ConsumptionLogListResponse(
            records=[
                ConsumptionLogResponse.model_validate(log) for log in logs
            ],
            total_count=total_count,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid datetime format. Use ISO strings.",
        )
    except Exception as exc:
        logger.error(
            f"Error listing consumption logs for user {current_user.id}: {exc}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving consumption logs",
        ) from exc


@router.post(
    "/",
    response_model=ConsumptionLogCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create consumption log",
    description="Create a new consumption log entry",
    responses={
        201: {"description": "Consumption log created successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        500: {"description": "Internal server error"},
    },
)
async def create_consumption_log(
    log_data: ConsumptionLogCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
) -> ConsumptionLogCreateResponse:
    """Create a new log for the current user."""
    try:
        nutrition_service = NutritionService(db)
        log = nutrition_service.create_consumption_log(
            user_id=current_user.id,
            log_data=log_data,
        )

        return ConsumptionLogCreateResponse(
            message="Consumption log created successfully",
            log=ConsumptionLogResponse.model_validate(log),
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            f"Error creating consumption log for user {current_user.id}: {exc}"
        )
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating consumption log",
        ) from exc


@router.get(
    "/{log_id}",
    response_model=ConsumptionLogResponse,
    summary="Get consumption log",
    description="Retrieve a single consumption log by ID",
    responses={
        200: {"description": "Consumption log retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Consumption log not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_consumption_log(
    log_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
) -> ConsumptionLogResponse:
    """Fetch a single consumption log."""
    try:
        nutrition_service = NutritionService(db)
        log = nutrition_service.get_consumption_log(current_user.id, log_id)
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consumption log not found",
            )
        return ConsumptionLogResponse.model_validate(log)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            f"Error retrieving consumption log {log_id} for user {current_user.id}: {exc}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving consumption log",
        ) from exc


@router.put(
    "/{log_id}",
    response_model=ConsumptionLogResponse,
    summary="Update consumption log",
    description="Update an existing consumption log entry",
    responses={
        200: {"description": "Consumption log updated successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Consumption log not found"},
        500: {"description": "Internal server error"},
    },
)
async def update_consumption_log(
    log_id: str,
    log_data: ConsumptionLogUpdate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
) -> ConsumptionLogResponse:
    """Update a consumption log."""
    try:
        nutrition_service = NutritionService(db)
        log = nutrition_service.get_consumption_log(current_user.id, log_id)
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consumption log not found",
            )

        updated_log = nutrition_service.update_consumption_log(log, log_data)
        return ConsumptionLogResponse.model_validate(updated_log)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            f"Error updating consumption log {log_id} for user {current_user.id}: {exc}"
        )
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating consumption log",
        ) from exc


@router.delete(
    "/{log_id}",
    response_model=ConsumptionLogDeleteResponse,
    summary="Delete consumption log",
    description="Delete a consumption log entry",
    responses={
        200: {"description": "Consumption log deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Consumption log not found"},
        500: {"description": "Internal server error"},
    },
)
async def delete_consumption_log(
    log_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
) -> ConsumptionLogDeleteResponse:
    """Delete a consumption log."""
    try:
        nutrition_service = NutritionService(db)
        log = nutrition_service.get_consumption_log(current_user.id, log_id)
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consumption log not found",
            )

        nutrition_service.delete_consumption_log(log)
        return ConsumptionLogDeleteResponse(
            message=f"Consumption log {log_id} deleted successfully",
            deleted_count=1,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            f"Error deleting consumption log {log_id} for user {current_user.id}: {exc}"
        )
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting consumption log",
        ) from exc
