import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.db.session import get_db
from app.models.auth.user import AuthUser
from app.models.metric.calories.baseline import CaloriesBaseline
from app.schemas.metric.calories.baseline import (
    CaloriesBaselineBulkCreate,
    CaloriesBaselineBulkCreateResponse,
    CaloriesBaselineDeleteResponse,
    CaloriesBaselineResponse,
)
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/baseline",
    tags=["metric-calories-baseline"],
)


@router.get("/", response_model=list[CaloriesBaselineResponse])
async def get_calories_baseline(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Get calories baseline data"""
    try:
        query = db.query(CaloriesBaseline).filter(
            CaloriesBaseline.user_id == current_user.id
        )

        # Apply date filters if provided
        if start_date:
            query = query.filter(CaloriesBaseline.date_hour >= start_date)
        if end_date:
            query = query.filter(CaloriesBaseline.date_hour <= end_date)

        records = query.order_by(CaloriesBaseline.date_hour.desc()).all()

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


@router.post("/bulk", response_model=CaloriesBaselineBulkCreateResponse)
async def create_or_update_multiple_baseline_calories_records(
    bulk_data: CaloriesBaselineBulkCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Create or update multiple baseline calories records (bulk upsert)"""
    try:
        created_count = 0
        updated_count = 0
        processed_records = []

        for baseline_data in bulk_data.records:
            # Check if record already exists for this date and source
            existing_record = (
                db.query(CaloriesBaseline)
                .filter(
                    CaloriesBaseline.user_id == current_user.id,
                    CaloriesBaseline.date_hour == baseline_data.date,
                    CaloriesBaseline.source == baseline_data.source,
                )
                .one_or_none()
            )

            if existing_record:
                # Update existing record
                if baseline_data.baseline_calories is not None:
                    setattr(
                        existing_record,
                        "baseline_calories",
                        baseline_data.baseline_calories,
                    )
                if baseline_data.bmr is not None:
                    setattr(existing_record, "bmr", baseline_data.bmr)
                setattr(existing_record, "updated_at", datetime.utcnow())
                processed_records.append(existing_record)
                updated_count += 1
            else:
                # Create new baseline calories record
                new_record = CaloriesBaseline(
                    id=generate_rid("metric", "calories_baseline"),
                    user_id=current_user.id,
                    date_hour=baseline_data.date,
                    baseline_calories=baseline_data.baseline_calories,
                    bmr=baseline_data.bmr,
                    source=baseline_data.source,
                )
                db.add(new_record)
                processed_records.append(new_record)
                created_count += 1

        # Commit all changes at once
        db.commit()

        logger.info(
            f"Bulk processed {len(bulk_data.records)} baseline calories records for {current_user.id}: "
            f"{created_count} created, {updated_count} updated"
        )

        return CaloriesBaselineBulkCreateResponse(
            message=f"Bulk operation completed: {created_count} created, {updated_count} updated",
            created_count=created_count,
            updated_count=updated_count,
            total_processed=len(bulk_data.records),
            records=processed_records,
        )

    except Exception as e:
        logger.error(f"Error in bulk upsert of baseline calories records: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in bulk upsert: {str(e)}",
        )


@router.get("/{record_id}", response_model=CaloriesBaselineResponse)
async def get_calories_baseline_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
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


@router.delete("/{record_id}", response_model=CaloriesBaselineDeleteResponse)
async def delete_calories_baseline_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
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
