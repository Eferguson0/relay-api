import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.db.session import get_db
from app.models.auth.user import AuthUser
from app.models.metric.body.composition import BodyComposition
from app.schemas.metric.body.composition import (
    BodyCompositionBulkCreate,
    BodyCompositionBulkCreateResponse,
    BodyCompositionDeleteResponse,
    BodyCompositionExportResponse,
    BodyCompositionResponse,
)
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/composition", tags=["metric-body-composition"])


@router.get("/")
async def get_body_composition(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: AuthUser = Depends(get_current_active_user),
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

        # Convert model objects to response objects
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


@router.post("/bulk", response_model=BodyCompositionBulkCreateResponse)
async def create_or_update_multiple_body_composition_records(
    bulk_data: BodyCompositionBulkCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Create or update multiple body composition records (bulk upsert)"""
    try:
        created_count = 0
        updated_count = 0
        processed_records = []

        for composition_data in bulk_data.records:
            # Check if record already exists for this user (one record per user for body composition)
            existing_record = (
                db.query(BodyComposition)
                .filter(BodyComposition.user_id == current_user.id)
                .one_or_none()
            )

            if existing_record:
                # Update existing record
                if composition_data.weight is not None:
                    setattr(existing_record, "weight", composition_data.weight)
                if composition_data.body_fat_percentage is not None:
                    setattr(
                        existing_record,
                        "body_fat_percentage",
                        composition_data.body_fat_percentage,
                    )
                if composition_data.muscle_mass_percentage is not None:
                    setattr(
                        existing_record,
                        "muscle_mass_percentage",
                        composition_data.muscle_mass_percentage,
                    )
                if composition_data.bone_density is not None:
                    setattr(
                        existing_record, "bone_density", composition_data.bone_density
                    )
                if composition_data.water_percentage is not None:
                    setattr(
                        existing_record,
                        "water_percentage",
                        composition_data.water_percentage,
                    )
                if composition_data.visceral_fat is not None:
                    setattr(
                        existing_record, "visceral_fat", composition_data.visceral_fat
                    )
                if composition_data.bmr is not None:
                    setattr(existing_record, "bmr", composition_data.bmr)
                if composition_data.measurement_method is not None:
                    setattr(
                        existing_record,
                        "measurement_method",
                        composition_data.measurement_method,
                    )
                if composition_data.notes is not None:
                    setattr(existing_record, "notes", composition_data.notes)
                setattr(existing_record, "updated_at", datetime.utcnow())
                processed_records.append(existing_record)
                updated_count += 1
            else:
                # Create new body composition record
                new_record = BodyComposition(
                    id=generate_rid("metric", "body_composition"),
                    user_id=current_user.id,
                    measurement_date=composition_data.measurement_date,
                    weight=composition_data.weight,
                    body_fat_percentage=composition_data.body_fat_percentage,
                    muscle_mass_percentage=composition_data.muscle_mass_percentage,
                    bone_density=composition_data.bone_density,
                    water_percentage=composition_data.water_percentage,
                    visceral_fat=composition_data.visceral_fat,
                    bmr=composition_data.bmr,
                    measurement_method=composition_data.measurement_method,
                    notes=composition_data.notes,
                )
                db.add(new_record)
                processed_records.append(new_record)
                created_count += 1

        # Commit all changes at once
        db.commit()

        logger.info(
            f"Bulk processed {len(bulk_data.records)} body composition records for {current_user.id}: "
            f"{created_count} created, {updated_count} updated"
        )

        return BodyCompositionBulkCreateResponse(
            message=f"Bulk operation completed: {created_count} created, {updated_count} updated",
            created_count=created_count,
            updated_count=updated_count,
            total_processed=len(bulk_data.records),
            records=processed_records,
        )

    except Exception as e:
        logger.error(f"Error in bulk upsert of body composition records: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in bulk upsert: {str(e)}",
        )


@router.delete("/{weight_id}", response_model=BodyCompositionDeleteResponse)
async def delete_body_composition_record(
    weight_id: str,
    current_user: AuthUser = Depends(get_current_active_user),
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
