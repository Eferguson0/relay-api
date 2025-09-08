import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.db.session import get_db
from app.models.auth.user import User
from app.models.metric.calories.baseline import CaloriesBaseline
from app.schemas.metric.calories.baseline_burn import (
    CaloriesBaselineCreate,
    CaloriesBaselineCreateResponse,
    CaloriesBaselineDeleteResponse,
    CaloriesBaselineResponse,
    CaloriesBaselineUpdate,
    CaloriesBaselineUpdateResponse,
)
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/metric/calories/baseline",
    tags=["metric-calories-baseline"],
)


@router.get("/", response_model=list[CaloriesBaselineResponse])
async def get_calories_baseline(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get calories baseline data"""
    try:
        query = db.query(CaloriesBaseline).filter(
            CaloriesBaseline.user_id == current_user.id
        )

        # Apply date filters if provided
        if start_date:
            query = query.filter(CaloriesBaseline.date >= start_date)
        if end_date:
            query = query.filter(CaloriesBaseline.date <= end_date)

        records = query.order_by(CaloriesBaseline.date.desc()).all()

        logger.info(
            f"Retrieved {len(records)} calories baseline records for {current_user.id}"
        )
        return records

    except Exception as e:
        logger.error(f"Error retrieving calories baseline: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving data: {str(e)}",
        )


@router.get("/{record_id}", response_model=CaloriesBaselineResponse)
async def get_calories_baseline_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific calories baseline record by ID"""
    try:
        record = (
            db.query(CaloriesBaseline)
            .filter(
                CaloriesBaseline.id == record_id,
                CaloriesBaseline.user_id == current_user.id,
            )
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calories baseline record not found",
            )

        logger.info(
            f"Retrieved calories baseline record {record_id} for {current_user.id}"
        )
        return record

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving calories baseline record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving record: {str(e)}",
        )


@router.post("/", response_model=CaloriesBaselineCreateResponse)
async def create_calories_baseline_record(
    baseline_data: CaloriesBaselineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new calories baseline record"""
    try:
        # Check if record already exists for this date and source
        existing_record = (
            db.query(CaloriesBaseline)
            .filter(
                CaloriesBaseline.user_id == current_user.id,
                CaloriesBaseline.date == baseline_data.date,
                CaloriesBaseline.source == baseline_data.source,
            )
            .first()
        )

        if existing_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Calories baseline record already exists for this date and source. Use PUT to update it.",
            )

        # Create new calories baseline record
        new_record = CaloriesBaseline(
            id=generate_rid("metric", "calories_baseline"),
            user_id=current_user.id,
            date=baseline_data.date,
            calories_burned=baseline_data.calories_burned,
            source=baseline_data.source,
            notes=baseline_data.notes,
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)

        logger.info(f"Created calories baseline record for {current_user.id}")
        return CaloriesBaselineCreateResponse(
            message="Calories baseline record created successfully", record=new_record
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating calories baseline record: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating record: {str(e)}",
        )


@router.put("/{record_id}", response_model=CaloriesBaselineUpdateResponse)
async def update_calories_baseline_record(
    record_id: str,
    baseline_data: CaloriesBaselineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update a calories baseline record"""
    try:
        # Find existing record
        record = (
            db.query(CaloriesBaseline)
            .filter(
                CaloriesBaseline.id == record_id,
                CaloriesBaseline.user_id == current_user.id,
            )
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calories baseline record not found to update",
            )

        # Update fields if provided
        if baseline_data.date is not None:
            record.date = baseline_data.date
        if baseline_data.calories_burned is not None:
            record.calories_burned = baseline_data.calories_burned
        if baseline_data.source is not None:
            record.source = baseline_data.source
        if baseline_data.notes is not None:
            record.notes = baseline_data.notes

        db.commit()
        db.refresh(record)

        logger.info(
            f"Updated calories baseline record {record_id} for {current_user.id}"
        )
        return CaloriesBaselineUpdateResponse(
            message="Calories baseline record updated successfully", record=record
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating calories baseline record: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating record: {str(e)}",
        )


@router.delete("/{record_id}", response_model=CaloriesBaselineDeleteResponse)
async def delete_calories_baseline_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a calories baseline record"""
    try:
        # Find and delete the record
        record = (
            db.query(CaloriesBaseline)
            .filter(
                CaloriesBaseline.id == record_id,
                CaloriesBaseline.user_id == current_user.id,
            )
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calories baseline record not found to delete",
            )

        db.delete(record)
        db.commit()

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
