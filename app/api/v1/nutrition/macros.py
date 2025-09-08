import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.db.session import get_db
from app.models.auth.user import User
from app.models.nutrition.macros import Diet
from app.schemas.nutrition.macros import (
    DailyAggregationResponse,
    DietDeleteResponse,
    DietExportResponse,
    DietIngestRequest,
    DietIngestResponse,
    DietRecordCreate,
    DietRecordResponse,
)
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/nutrition/macros", tags=["nutrition-macros"])


@router.get("/")
async def get_macros_data(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    meal_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get macro records with optional filtering"""
    try:
        # Only show data for the authenticated user (security)
        query = db.query(Diet).filter(Diet.user_id == current_user.id)

        # Filter by date range if provided
        if start_date:
            query = query.filter(Diet.datetime >= start_date)
        if end_date:
            query = query.filter(Diet.datetime <= end_date)

        # Filter by meal name if provided
        if meal_name:
            query = query.filter(Diet.meal_name.ilike(f"%{meal_name}%"))

        # Order by datetime descending
        query = query.order_by(Diet.datetime.desc())

        records = query.all()

        # Calculate totals
        total_calories = sum(record.calories for record in records if record.calories)
        total_protein = sum(record.protein for record in records if record.protein)
        total_carbs = sum(record.carbs for record in records if record.carbs)
        total_fat = sum(record.fat for record in records if record.fat)

        return DietExportResponse(
            records=records,
            total_count=len(records),
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


@router.post("/", response_model=DietIngestResponse)
async def ingest_macros_data(
    request: DietIngestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Ingest macro data and store in diet table"""
    try:
        # Use the authenticated user
        user = current_user

        # Process the diet data from request body
        inserted_records = 0
        total_calories = 0.0
        total_protein = 0.0
        total_carbs = 0.0
        total_fat = 0.0

        # Process each macro data point
        for data_point in request.data:
            try:
                # Parse datetime
                meal_datetime = datetime.fromisoformat(
                    data_point.datetime.replace("Z", "+00:00")
                )

                # Create new diet record
                new_record = Diet(
                    id=generate_rid("nutrition", "macros"),
                    user_id=user.id,
                    datetime=meal_datetime,
                    protein=data_point.protein,
                    carbs=data_point.carbs,
                    fat=data_point.fat,
                    calories=data_point.calories,
                    meal_name=data_point.meal_name,
                    notes=data_point.notes,
                )
                db.add(new_record)
                inserted_records += 1

                # Add to totals
                if data_point.calories:
                    total_calories += data_point.calories
                if data_point.protein:
                    total_protein += data_point.protein
                if data_point.carbs:
                    total_carbs += data_point.carbs
                if data_point.fat:
                    total_fat += data_point.fat

                logger.info(f"Added macro record for {meal_datetime}")

            except Exception as e:
                logger.error(f"Error processing macro data point: {str(e)}")
                continue

        # Commit all changes
        db.commit()

        logger.info(f"Successfully ingested {inserted_records} macro records")

        return DietIngestResponse(
            message="Macro data ingested successfully",
            records_processed=inserted_records,
            user_id=user.id,
            total_calories=total_calories if total_calories > 0 else None,
            total_protein=total_protein if total_protein > 0 else None,
            total_carbs=total_carbs if total_carbs > 0 else None,
            total_fat=total_fat if total_fat > 0 else None,
        )

    except Exception as e:
        logger.error(f"Error ingesting macro data: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting data: {str(e)}",
        )


@router.post("/record", response_model=DietRecordResponse)
async def add_macro_record(
    record_data: DietRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Add a single macro record"""
    try:
        # Parse datetime
        meal_datetime = datetime.fromisoformat(
            record_data.datetime.replace("Z", "+00:00")
        )

        # Create new diet record
        new_record = Diet(
            id=generate_rid("nutrition", "macros"),
            user_id=current_user.id,
            datetime=meal_datetime,
            protein=record_data.protein,
            carbs=record_data.carbs,
            fat=record_data.fat,
            calories=record_data.calories,
            meal_name=record_data.meal_name,
            notes=record_data.notes,
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)

        logger.info(f"Added macro record for {current_user.id} at {meal_datetime}")
        return new_record

    except Exception as e:
        logger.error(f"Error adding macro record: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding record: {str(e)}",
        )


@router.delete("/record/{record_id}", response_model=DietDeleteResponse)
async def delete_macro_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a macro record by ID"""
    try:
        # Find the record and ensure it belongs to the current user
        record = (
            db.query(Diet)
            .filter(Diet.id == record_id, Diet.user_id == current_user.id)
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
        return DietDeleteResponse(
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
    current_user: User = Depends(get_current_active_user),
):
    """Get all macro records for a specific day"""
    try:
        # Parse the date
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())

        # Get all records for the day
        records = (
            db.query(Diet)
            .filter(
                Diet.user_id == current_user.id,
                Diet.datetime >= start_datetime,
                Diet.datetime <= end_datetime,
            )
            .order_by(Diet.datetime.asc())
            .all()
        )

        # Calculate totals
        total_calories = sum(record.calories for record in records if record.calories)
        total_protein = sum(record.protein for record in records if record.protein)
        total_carbs = sum(record.carbs for record in records if record.carbs)
        total_fat = sum(record.fat for record in records if record.fat)

        # Create daily aggregation
        daily_aggregation = {
            "date": date,
            "total_calories": total_calories if total_calories > 0 else None,
            "total_protein": total_protein if total_protein > 0 else None,
            "total_carbs": total_carbs if total_carbs > 0 else None,
            "total_fat": total_fat if total_fat > 0 else None,
            "meal_count": len(records),
            "meals": records,
        }

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
    current_user: User = Depends(get_current_active_user),
):
    """Get aggregated macro records by day"""
    try:
        query = db.query(Diet).filter(Diet.user_id == current_user.id)

        # Apply date filters if provided
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(
                Diet.datetime >= datetime.combine(start_dt, datetime.min.time())
            )

        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(
                Diet.datetime <= datetime.combine(end_dt, datetime.max.time())
            )

        # Get all records
        records = query.order_by(Diet.datetime.asc()).all()

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
