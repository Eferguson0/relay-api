import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.db.session import get_db
from app.models.auth.user import AuthUser
from app.models.metric.calories.active import CaloriesActive
from app.schemas.metric.calories.active import (
    ActiveCaloriesExportRecord,
    ActiveCaloriesExportResponse,
    CaloriesActiveBulkCreate,
    CaloriesActiveBulkCreateResponse,
    CaloriesActiveDeleteResponse,
    CaloriesActiveResponse,
)
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/active", tags=["metric-calories-active"])


@router.get("/", response_model=ActiveCaloriesExportResponse)
async def get_active_calories_burn(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: AuthUser = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get active calories burn data"""
    try:
        # Only show data for the authenticated user (security)
        query = db.query(CaloriesActive).filter(
            CaloriesActive.user_id == current_user.id
        )

        # Apply date filters if provided
        if start_date:
            query = query.filter(CaloriesActive.date_hour >= start_date)
        if end_date:
            query = query.filter(CaloriesActive.date_hour <= end_date)

        # Execute query and convert to response objects
        records = query.order_by(CaloriesActive.date_hour.desc()).all()

        # Convert model objects to response objects
        response_records = [
            ActiveCaloriesExportRecord.model_validate(record) for record in records
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


@router.post("/bulk", response_model=CaloriesActiveBulkCreateResponse)
async def create_or_update_multiple_active_calories_records(
    bulk_data: CaloriesActiveBulkCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Create or update multiple active calories records (bulk upsert)"""
    try:
        created_count = 0
        updated_count = 0
        processed_records = []

        for calories_data in bulk_data.records:
            # Check if record already exists for this date and source
            existing_record = (
                db.query(CaloriesActive)
                .filter(
                    CaloriesActive.user_id == current_user.id,
                    CaloriesActive.date_hour == calories_data.date_hour,
                    CaloriesActive.source == calories_data.source,
                )
                .one_or_none()
            )

            if existing_record:
                # Update existing record
                if calories_data.calories_burned is not None:
                    setattr(
                        existing_record,
                        "calories_burned",
                        calories_data.calories_burned,
                    )
                setattr(existing_record, "updated_at", datetime.utcnow())
                processed_records.append(existing_record)
                updated_count += 1
            else:
                # Create new active calories record
                new_record = CaloriesActive(
                    id=generate_rid("metric", "active_calories"),
                    user_id=current_user.id,
                    date_hour=calories_data.date_hour,
                    calories_burned=calories_data.calories_burned,
                    source=calories_data.source,
                )
                db.add(new_record)
                processed_records.append(new_record)
                created_count += 1

        # Commit all changes at once
        db.commit()

        logger.info(
            f"Bulk processed {len(bulk_data.records)} active calories records for {current_user.id}: "
            f"{created_count} created, {updated_count} updated"
        )

        return CaloriesActiveBulkCreateResponse(
            message=f"Bulk operation completed: {created_count} created, {updated_count} updated",
            created_count=created_count,
            updated_count=updated_count,
            total_processed=len(bulk_data.records),
            records=processed_records,
        )

    except Exception as e:
        logger.error(f"Error in bulk upsert of active calories records: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in bulk upsert: {str(e)}",
        )


@router.get("/{record_id}", response_model=CaloriesActiveResponse)
async def get_active_calories_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Get a specific active calories record by ID"""
    try:
        record = (
            db.query(CaloriesActive)
            .filter(
                CaloriesActive.id == record_id,
                CaloriesActive.user_id == current_user.id,
            )
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active calories record not found",
            )

        logger.info(
            f"Retrieved active calories record {record_id} for {current_user.id}"
        )
        return record

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving active calories record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving record: {str(e)}",
        )


@router.delete("/{record_id}", response_model=CaloriesActiveDeleteResponse)
async def delete_active_calories_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Delete an active calories record"""
    try:
        # Find and delete the record
        record = (
            db.query(CaloriesActive)
            .filter(
                CaloriesActive.id == record_id,
                CaloriesActive.user_id == current_user.id,
            )
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active calories record not found to delete",
            )

        db.delete(record)
        db.commit()

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
