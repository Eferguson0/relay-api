import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.weight import Weight
from app.models.user import User
from app.schemas.weight import (
    WeightCreate,
    WeightUpdate,
    WeightResponse,
    WeightCreateResponse,
    WeightUpdateResponse,
    WeightDeleteResponse,
    WeightExportResponse,
)
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["weight"])


@router.post("/weight", response_model=WeightCreateResponse)
async def create_weight_record(
    weight_data: WeightCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new weight measurement record"""
    try:
        # Create new weight record
        new_weight = Weight(
            user_email=current_user.email,
            weight=weight_data.weight,
            body_fat_percentage=weight_data.body_fat_percentage,
            muscle_mass_percentage=weight_data.muscle_mass_percentage,
            notes=weight_data.notes,
        )
        db.add(new_weight)
        db.commit()
        db.refresh(new_weight)

        logger.info(f"Created weight record for {current_user.email}")
        return WeightCreateResponse(
            message="Weight record created successfully", weight=new_weight
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating weight record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create weight record",
        )


@router.get("/weight", response_model=WeightExportResponse)
async def get_weight_records(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get all weight records for the current user"""
    try:
        weights = (
            db.query(Weight)
            .filter(Weight.user_email == current_user.email)
            .order_by(Weight.created_at.desc())
            .all()
        )

        logger.info(f"Retrieved {len(weights)} weight records for {current_user.email}")
        return WeightExportResponse(
            records=weights, total_count=len(weights), user_email=current_user.email
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving weight records: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve weight records",
        )


@router.get("/weight/{weight_id}", response_model=WeightResponse)
async def get_weight_record(
    weight_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get a specific weight record by ID"""
    try:
        weight = (
            db.query(Weight)
            .filter(Weight.id == weight_id, Weight.user_email == current_user.email)
            .first()
        )

        if not weight:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Weight record not found",
            )

        logger.info(f"Retrieved weight record {weight_id} for {current_user.email}")
        return weight

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving weight record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve weight record",
        )


@router.put("/weight/{weight_id}", response_model=WeightUpdateResponse)
async def update_weight_record(
    weight_id: int,
    weight_data: WeightUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update a specific weight record"""
    try:
        # Find existing weight record
        weight = (
            db.query(Weight)
            .filter(Weight.id == weight_id, Weight.user_email == current_user.email)
            .first()
        )

        if not weight:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Weight record not found",
            )

        # Update fields if provided
        if weight_data.weight is not None:
            weight.weight = weight_data.weight
        if weight_data.body_fat_percentage is not None:
            weight.body_fat_percentage = weight_data.body_fat_percentage
        if weight_data.muscle_mass_percentage is not None:
            weight.muscle_mass_percentage = weight_data.muscle_mass_percentage
        if weight_data.notes is not None:
            weight.notes = weight_data.notes

        db.commit()
        db.refresh(weight)

        logger.info(f"Updated weight record {weight_id} for {current_user.email}")
        return WeightUpdateResponse(
            message="Weight record updated successfully", weight=weight
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating weight record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update weight record",
        )


@router.delete("/weight/{weight_id}", response_model=WeightDeleteResponse)
async def delete_weight_record(
    weight_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a specific weight record"""
    try:
        # Find and delete the weight record
        weight = (
            db.query(Weight)
            .filter(Weight.id == weight_id, Weight.user_email == current_user.email)
            .first()
        )

        if not weight:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Weight record not found",
            )

        db.delete(weight)
        db.commit()

        logger.info(f"Deleted weight record {weight_id} for {current_user.email}")
        return WeightDeleteResponse(
            message="Weight record deleted successfully", deleted_count=1
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting weight record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete weight record",
        )
