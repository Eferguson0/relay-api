import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.db.session import get_db
from app.models.auth.user import User
from app.models.metric.body.composition import BodyComposition
from app.schemas.metric.body.composition import (
    BodyCompositionCreate,
    BodyCompositionCreateResponse,
    BodyCompositionDeleteResponse,
    BodyCompositionExportResponse,
)
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/metric/body/composition", tags=["metric-body-composition"]
)


@router.get("/")
async def get_body_composition(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get body composition data (weight, body fat, muscle mass)"""
    try:
        # Only show data for the authenticated user (security)
        query = db.query(BodyComposition).filter(
            BodyComposition.user_id == current_user.id
        )

        # Filter by date range if provided
        if start_date:
            query = query.filter(BodyComposition.created_at >= start_date)
        if end_date:
            query = query.filter(BodyComposition.created_at <= end_date)

        # Order by created_at descending
        query = query.order_by(BodyComposition.created_at.desc())

        records = query.all()

        return BodyCompositionExportResponse(
            records=records,
            total_count=len(records),
            user_id=current_user.id,
        )

    except Exception as e:
        logger.error(f"Error fetching body composition records: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching data: {str(e)}",
        )


@router.post("/", response_model=BodyCompositionCreateResponse)
async def create_or_update_body_composition_record(
    weight_data: BodyCompositionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create or update a body composition measurement record (upsert)"""
    try:
        # Check if record already exists for this user (one record per user for body composition)
        existing_record = (
            db.query(BodyComposition)
            .filter(BodyComposition.user_id == current_user.id)
            .first()
        )

        if existing_record:
            # Update existing record
            if weight_data.weight is not None:
                existing_record.weight = weight_data.weight
            if weight_data.body_fat_percentage is not None:
                existing_record.body_fat_percentage = weight_data.body_fat_percentage
            if weight_data.muscle_mass_percentage is not None:
                existing_record.muscle_mass_percentage = (
                    weight_data.muscle_mass_percentage
                )
            if weight_data.notes is not None:
                existing_record.notes = weight_data.notes

            db.commit()
            db.refresh(existing_record)

            logger.info(f"Updated body composition record for {current_user.id}")
            return BodyCompositionCreateResponse(
                message="Body composition record updated successfully",
                weight=existing_record,
            )
        else:
            # Create new weight record
            new_weight = BodyComposition(
                id=generate_rid("metric", "body_composition"),
                user_id=current_user.id,
                weight=weight_data.weight,
                body_fat_percentage=weight_data.body_fat_percentage,
                muscle_mass_percentage=weight_data.muscle_mass_percentage,
                notes=weight_data.notes,
            )
            db.add(new_weight)
            db.commit()
            db.refresh(new_weight)

            logger.info(f"Created body composition record for {current_user.id}")
            return BodyCompositionCreateResponse(
                message="Body composition record created successfully",
                weight=new_weight,
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating/updating body composition record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create/update body composition record",
        )


@router.delete("/{weight_id}", response_model=BodyCompositionDeleteResponse)
async def delete_body_composition_record(
    weight_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a body composition measurement record"""
    try:
        # Find the weight record and ensure it belongs to the current user
        weight_record = (
            db.query(BodyComposition)
            .filter(
                BodyComposition.id == weight_id,
                BodyComposition.user_id == current_user.id,
            )
            .first()
        )

        if not weight_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="BodyComposition record not found or you don't have permission to delete it",
            )

        db.delete(weight_record)
        db.commit()

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
