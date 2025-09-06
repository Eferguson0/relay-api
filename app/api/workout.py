import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.workout import ActiveCalories, HourlySteps
from app.schemas.workout import (
    ActiveCaloriesExportResponse,
    ActiveCaloriesIngestRequest,
    ActiveCaloriesIngestResponse,
    HourlyStepsExportResponse,
    HourlyStepsIngestRequest,
    HourlyStepsIngestResponse,
)
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["workout"])


# Active Calories Endpoints
@router.post("/ingest-active-calories", response_model=ActiveCaloriesIngestResponse)
async def ingest_active_calories_data(
    request: ActiveCaloriesIngestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Ingest active calories data from request body and store in active_calories table"""
    try:
        # Use the authenticated user
        user = current_user

        # Process the active calories data from request body
        records_processed = 0
        metrics_processed = []

        for metric in request.record.data.metrics:
            if metric.name != "active_calories":
                continue

            metrics_processed.append(metric.name)

            for data_point in metric.data:
                # Parse the date string
                try:
                    # Handle different date formats
                    date_str = data_point.date
                    if "T" in date_str:
                        # ISO format with time
                        meal_datetime = datetime.fromisoformat(
                            date_str.replace("Z", "+00:00")
                        )
                    else:
                        # Date only format
                        meal_datetime = datetime.fromisoformat(date_str)
                except ValueError as e:
                    logger.warning(f"Invalid date format: {date_str}, error: {e}")
                    continue

                source = data_point.source
                if not source:
                    continue

                # Check if record already exists (upsert behavior)
                existing_record = (
                    db.query(ActiveCalories)
                    .filter(
                        ActiveCalories.user_id == user.id,
                        ActiveCalories.date == meal_datetime,
                        ActiveCalories.source == source,
                    )
                    .first()
                )

                if existing_record:
                    # Update existing record
                    existing_record.calories_burned = data_point.calories_burned
                    existing_record.updated_at = datetime.utcnow()
                else:
                    # Create new record
                    new_record = ActiveCalories(
                        user_id=user.id,
                        date=meal_datetime,
                        calories_burned=data_point.calories_burned,
                        source=source,
                    )
                    db.add(new_record)

                records_processed += 1

        db.commit()

        logger.info(
            f"Processed {records_processed} active calories records for user {user.id}"
        )

        return ActiveCaloriesIngestResponse(
            message="Active calories data ingested successfully",
            records_processed=records_processed,
            metrics_processed=metrics_processed,
            user_id=user.id,
            source="POST request",
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Error ingesting active calories data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting data: {str(e)}",
        )


@router.get("/active-calories", response_model=ActiveCaloriesExportResponse)
async def get_active_calories_data(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get hourly active calories records with optional filtering"""
    try:
        # Only show data for the authenticated user (security)
        query = db.query(ActiveCalories).filter(
            ActiveCalories.user_id == current_user.id
        )

        # Apply date filters if provided
        if start_date:
            query = query.filter(ActiveCalories.date >= start_date)
        if end_date:
            query = query.filter(ActiveCalories.date <= end_date)

        # Execute query and convert to list of dictionaries
        records = query.order_by(ActiveCalories.date.desc()).all()
        records_data = [
            {
                "user_id": record.user_id,
                "date": record.date.isoformat(),
                "calories_burned": (
                    float(record.calories_burned) if record.calories_burned else None
                ),
                "source": record.source,
                "created_at": (
                    record.created_at.isoformat() if record.created_at else None
                ),
                "updated_at": (
                    record.updated_at.isoformat() if record.updated_at else None
                ),
            }
            for record in records
        ]

        return ActiveCaloriesExportResponse(
            records=records_data,
            total_count=len(records_data),
            user_id=current_user.id,
        )

    except Exception as e:
        logger.error(f"Error retrieving active calories data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve active calories records",
        )


# Hourly Steps Endpoints
@router.post("/ingest-hourly-steps", response_model=HourlyStepsIngestResponse)
async def ingest_hourly_steps_data(
    request: HourlyStepsIngestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Ingest hourly steps data from request body and store in hourly_steps table"""
    try:
        # Use the authenticated user
        user = current_user

        # Process the hourly steps data from request body
        records_processed = 0
        metrics_processed = []

        for metric in request.record.data.metrics:
            if metric.name != "hourly_steps":
                continue

            metrics_processed.append(metric.name)

            for data_point in metric.data:
                # Parse the date string
                try:
                    # Handle different date formats
                    date_str = data_point.date
                    if "T" in date_str:
                        # ISO format with time
                        meal_datetime = datetime.fromisoformat(
                            date_str.replace("Z", "+00:00")
                        )
                    else:
                        # Date only format
                        meal_datetime = datetime.fromisoformat(date_str)
                except ValueError as e:
                    logger.warning(f"Invalid date format: {date_str}, error: {e}")
                    continue

                source = data_point.source
                if not source:
                    continue

                # Check if record already exists (upsert behavior)
                existing_record = (
                    db.query(HourlySteps)
                    .filter(
                        HourlySteps.user_id == user.id,
                        HourlySteps.date == meal_datetime,
                        HourlySteps.source == source,
                    )
                    .first()
                )

                if existing_record:
                    # Update existing record
                    existing_record.steps = data_point.steps
                    existing_record.updated_at = datetime.utcnow()
                else:
                    # Create new record
                    new_record = HourlySteps(
                        user_id=user.id,
                        date=meal_datetime,
                        steps=data_point.steps,
                        source=source,
                    )
                    db.add(new_record)

                records_processed += 1

        db.commit()

        logger.info(
            f"Processed {records_processed} hourly steps records for user {user.id}"
        )

        return HourlyStepsIngestResponse(
            message="Hourly steps data ingested successfully",
            records_processed=records_processed,
            metrics_processed=metrics_processed,
            user_id=user.id,
            source="POST request",
        )

    except Exception as e:
        db.rollback()
        logger.error(f"Error ingesting hourly steps data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting data: {str(e)}",
        )


@router.get("/hourly-steps", response_model=HourlyStepsExportResponse)
async def get_hourly_steps_data(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get hourly steps records with optional filtering"""
    try:
        # Only show data for the authenticated user (security)
        query = db.query(HourlySteps).filter(HourlySteps.user_id == current_user.id)

        # Apply date filters if provided
        if start_date:
            query = query.filter(HourlySteps.date >= start_date)
        if end_date:
            query = query.filter(HourlySteps.date <= end_date)

        # Execute query and convert to list of dictionaries
        records = query.order_by(HourlySteps.date.desc()).all()
        records_data = [
            {
                "user_id": record.user_id,
                "date": record.date.isoformat(),
                "steps": record.steps,
                "source": record.source,
                "created_at": (
                    record.created_at.isoformat() if record.created_at else None
                ),
                "updated_at": (
                    record.updated_at.isoformat() if record.updated_at else None
                ),
            }
            for record in records
        ]

        return HourlyStepsExportResponse(
            records=records_data,
            total_count=len(records_data),
            user_id=current_user.id,
        )

    except Exception as e:
        logger.error(f"Error retrieving hourly steps data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve hourly steps records",
        )
