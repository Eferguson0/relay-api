import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.db.session import get_db
from app.models.auth.user import AuthUser
from app.models.nutrition.macros import NutritionMacros
from app.schemas.nutrition.macros import (
    DailyAggregation,
    DailyAggregationResponse,
    NutritionMacrosBulkCreate,
    NutritionMacrosBulkCreateResponse,
    NutritionMacrosDeleteResponse,
    NutritionMacrosExportResponse,
    NutritionMacrosRecord,
)
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/macros", tags=["nutrition-macros"])


@router.get("/", response_model=NutritionMacrosExportResponse)
async def get_macros_data(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    meal_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Get macro records with optional filtering"""
    try:
        # Only show data for the authenticated user (security)
        query = db.query(NutritionMacros).filter(
            NutritionMacros.user_id == current_user.id
        )

        # Filter by date range if provided
        if start_date:
            query = query.filter(NutritionMacros.datetime >= start_date)
        if end_date:
            query = query.filter(NutritionMacros.datetime <= end_date)

        # Filter by meal name if provided
        if meal_name:
            query = query.filter(NutritionMacros.meal_name.ilike(f"%{meal_name}%"))

        # Order by datetime descending
        query = query.order_by(NutritionMacros.datetime.desc())

        records = query.all()

        # Calculate totals
        total_calories = 0.0
        total_protein = 0.0
        total_carbs = 0.0
        total_fat = 0.0

        for record in records:
            if record.calories is not None:
                total_calories += float(record.calories)  # type: ignore
            if record.protein is not None:
                total_protein += float(record.protein)  # type: ignore
            if record.carbs is not None:
                total_carbs += float(record.carbs)  # type: ignore
            if record.fat is not None:
                total_fat += float(record.fat)  # type: ignore

        # Convert model objects to response objects
        response_records = [
            NutritionMacrosRecord.model_validate(record) for record in records
        ]

        return NutritionMacrosExportResponse(
            records=response_records,
            total_count=len(response_records),
            total_calories=total_calories if total_calories > 0 else None,
            total_protein=total_protein if total_protein > 0 else None,
            total_carbs=total_carbs if total_carbs > 0 else None,
            total_fat=total_fat if total_fat > 0 else None,
        )

    except Exception as e:
        logger.error(f"Error fetching macro records: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching data: {str(e)}",
        )


@router.post("/bulk", response_model=NutritionMacrosBulkCreateResponse)
async def create_or_update_multiple_macro_records(
    bulk_data: NutritionMacrosBulkCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Create or update multiple macro records (bulk upsert)"""
    try:
        created_count = 0
        updated_count = 0
        processed_records = []

        for record_data in bulk_data.records:
            # Check if record already exists for this datetime and meal_name
            existing_record = (
                db.query(NutritionMacros)
                .filter(
                    NutritionMacros.user_id == current_user.id,
                    NutritionMacros.datetime == record_data.datetime,
                    NutritionMacros.meal_name == record_data.meal_name,
                )
                .one_or_none()
            )

            if existing_record:
                # Update existing record
                if record_data.protein is not None:
                    setattr(existing_record, "protein", record_data.protein)
                if record_data.carbs is not None:
                    setattr(existing_record, "carbs", record_data.carbs)
                if record_data.fat is not None:
                    setattr(existing_record, "fat", record_data.fat)
                if record_data.calories is not None:
                    setattr(existing_record, "calories", record_data.calories)
                if record_data.notes is not None:
                    setattr(existing_record, "notes", record_data.notes)
                setattr(existing_record, "updated_at", datetime.utcnow())
                processed_records.append(existing_record)
                updated_count += 1
            else:
                # Create new macro record
                new_record = NutritionMacros(
                    id=generate_rid("nutrition", "macros"),
                    user_id=current_user.id,
                    datetime=record_data.datetime,
                    protein=record_data.protein,
                    carbs=record_data.carbs,
                    fat=record_data.fat,
                    calories=record_data.calories,
                    meal_name=record_data.meal_name,
                    notes=record_data.notes,
                )
                db.add(new_record)
                processed_records.append(new_record)
                created_count += 1

        # Commit all changes at once
        db.commit()

        logger.info(
            f"Bulk processed {len(bulk_data.records)} macro records for {current_user.id}: "
            f"{created_count} created, {updated_count} updated"
        )

        return NutritionMacrosBulkCreateResponse(
            message=f"Bulk operation completed: {created_count} created, {updated_count} updated",
            created_count=created_count,
            updated_count=updated_count,
            total_processed=len(bulk_data.records),
            records=processed_records,
        )

    except Exception as e:
        logger.error(f"Error in bulk upsert of macro records: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in bulk upsert: {str(e)}",
        )


@router.get("/{record_id}", response_model=NutritionMacrosRecord)
async def get_macro_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Get a specific macro record by ID"""
    try:
        record = (
            db.query(NutritionMacros)
            .filter(
                NutritionMacros.id == record_id,
                NutritionMacros.user_id == current_user.id,
            )
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Macro record not found",
            )

        logger.info(f"Retrieved macro record {record_id} for {current_user.id}")
        return record

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving macro record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving record: {str(e)}",
        )


@router.delete("/{record_id}", response_model=NutritionMacrosDeleteResponse)
async def delete_macro_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Delete a macro record by ID"""
    try:
        # Find the record and ensure it belongs to the current user
        record = (
            db.query(NutritionMacros)
            .filter(
                NutritionMacros.id == record_id,
                NutritionMacros.user_id == current_user.id,
            )
            .first()
        )

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Record not found or you don't have permission to delete it",
            )

        db.delete(record)
        db.commit()

        logger.info(f"Deleted macro record {record_id} for user {current_user.id}")
        return NutritionMacrosDeleteResponse(
            message="Record deleted successfully", deleted_count=1
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting macro record: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting record: {str(e)}",
        )


@router.get("/daily/{date}", response_model=DailyAggregationResponse)
async def get_daily_macro_records(
    date: str,  # Format: YYYY-MM-DD
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Get all macro records for a specific day"""
    try:
        # Parse the date
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())

        # Get all records for the day
        records = (
            db.query(NutritionMacros)
            .filter(
                NutritionMacros.user_id == current_user.id,
                NutritionMacros.datetime >= start_datetime,
                NutritionMacros.datetime <= end_datetime,
            )
            .order_by(NutritionMacros.datetime.asc())
            .all()
        )

        # Calculate totals
        total_calories = 0.0
        total_protein = 0.0
        total_carbs = 0.0
        total_fat = 0.0

        for record in records:
            if record.calories is not None:
                total_calories += float(record.calories)  # type: ignore
            if record.protein is not None:
                total_protein += float(record.protein)  # type: ignore
            if record.carbs is not None:
                total_carbs += float(record.carbs)  # type: ignore
            if record.fat is not None:
                total_fat += float(record.fat)  # type: ignore

        # Convert model objects to response objects
        response_records = [
            NutritionMacrosRecord.model_validate(record) for record in records
        ]

        # Create daily aggregation
        daily_aggregation = DailyAggregation(
            date=date,
            total_calories=total_calories if total_calories > 0 else None,
            total_protein=total_protein if total_protein > 0 else None,
            total_carbs=total_carbs if total_carbs > 0 else None,
            total_fat=total_fat if total_fat > 0 else None,
            meal_count=len(records),
            meals=response_records,
        )

        logger.info(f"Retrieved {len(records)} macro records for {date}")
        return DailyAggregationResponse(
            date=date, aggregations=[daily_aggregation], total_days=1
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD",
        )
    except Exception as e:
        logger.error(f"Error fetching daily macro records: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching daily records: {str(e)}",
        )


@router.get("/aggregate", response_model=DailyAggregationResponse)
async def get_macro_aggregations(
    start_date: Optional[str] = None,  # Format: YYYY-MM-DD
    end_date: Optional[str] = None,  # Format: YYYY-MM-DD
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Get aggregated macro records by day"""
    try:
        query = db.query(NutritionMacros).filter(
            NutritionMacros.user_id == current_user.id
        )

        # Apply date filters if provided
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(
                NutritionMacros.datetime
                >= datetime.combine(start_dt, datetime.min.time())
            )

        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(
                NutritionMacros.datetime
                <= datetime.combine(end_dt, datetime.max.time())
            )

        # Get all records
        records = query.order_by(NutritionMacros.datetime.asc()).all()

        # Group by date
        daily_groups = {}
        for record in records:
            date_key = record.datetime.date().strftime("%Y-%m-%d")
            if date_key not in daily_groups:
                daily_groups[date_key] = []
            daily_groups[date_key].append(record)

        # Create aggregations
        aggregations = []
        for date_str, day_records in daily_groups.items():
            total_calories = sum(
                record.calories for record in day_records if record.calories
            )
            total_protein = sum(
                record.protein for record in day_records if record.protein
            )
            total_carbs = sum(record.carbs for record in day_records if record.carbs)
            total_fat = sum(record.fat for record in day_records if record.fat)

            aggregations.append(
                {
                    "date": date_str,
                    "total_calories": total_calories if total_calories > 0 else None,
                    "total_protein": total_protein if total_protein > 0 else None,
                    "total_carbs": total_carbs if total_carbs > 0 else None,
                    "total_fat": total_fat if total_fat > 0 else None,
                    "meal_count": len(day_records),
                    "meals": day_records,
                }
            )

        # Sort by date
        aggregations.sort(key=lambda x: x["date"])

        logger.info(f"Retrieved aggregations for {len(aggregations)} days")
        return DailyAggregationResponse(
            date=f"{start_date or 'all'} to {end_date or 'all'}",
            aggregations=aggregations,
            total_days=len(aggregations),
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD",
        )
    except Exception as e:
        logger.error(f"Error fetching macro aggregations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching aggregations: {str(e)}",
        )
