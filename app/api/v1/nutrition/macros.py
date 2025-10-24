import logging
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.auth.user import AuthUser
from app.schemas.nutrition.macros import (
    DailyAggregation,
    DailyAggregationResponse,
    NutritionMacrosBulkCreate,
    NutritionMacrosBulkCreateResponse,
    NutritionMacrosDeleteResponse,
    NutritionMacrosRecord,
    NutritionMacrosExportResponse,
)
from app.services.auth_service import get_current_active_user
from app.services.nutrition_service import NutritionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/macros", tags=["nutrition-macros"])


@router.get("/",
    response_model=NutritionMacrosExportResponse,
    summary="Get macro records endpoint",
    description="Get macro records",
    responses={
        200: {"description": "Macro records retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        500: {"description": "Internal server error"},
    }
)
async def get_macros_data(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    meal_name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Get macro records with optional filtering"""
    try:

        nutrition_service = NutritionService(db)
        data = nutrition_service.get_macros_export_data(current_user.id, start_date, end_date, meal_name)


        if not data.records:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No macro records found",
            )
        return NutritionMacrosExportResponse(
            records=[NutritionMacrosRecord.model_validate(record) for record in data.records],
            total_count=data.total_count,
            total_calories=data.total_calories,
            total_protein=data.total_protein,
            total_carbs=data.total_carbs,
            total_fat=data.total_fat,
        )

    except Exception as e:
        logger.error(f"Error fetching macro records: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching data: {str(e)}",
        )


@router.post("/bulk",
    response_model=NutritionMacrosBulkCreateResponse,
    summary="Create or update multiple macro records (bulk upsert)",
    description="Create or update multiple macro records (bulk upsert)",
    responses={
        200: {"description": "Macro records created or updated successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        500: {"description": "Internal server error"},
    }
)
async def create_or_update_multiple_macro_records(
    bulk_data: NutritionMacrosBulkCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Create or update multiple macro records (bulk upsert)"""
    try:
        nutrition_service = NutritionService(db)
        processed_records, created_count, updated_count = nutrition_service.create_or_update_multiple_macro_records(bulk_data, current_user.id)

        return NutritionMacrosBulkCreateResponse(
            message="Macro records created or updated successfully",
            created_count=created_count,
            updated_count=updated_count,
            total_processed=len(processed_records),
            records=[NutritionMacrosRecord.model_validate(record) for record in processed_records],
        )

    except Exception as e:
        logger.error(f"Error in bulk upsert of macro records: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in bulk upsert: {str(e)}",
        )


@router.get("/{record_id}",
    response_model=NutritionMacrosRecord,
    summary="Get a specific macro record by ID",
    description="Get a specific macro record by ID",
    responses={
        200: {"description": "Macro record retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Macro record not found"},
    }
)
async def get_macro_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """Get a specific macro record by ID"""
    try:
        nutrition_service = NutritionService(db)
        record = nutrition_service.get_macro_record(current_user.id, record_id)
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Macro record not found",
            )

        logger.info(f"Retrieved macro record {record_id} for {current_user.id}")
        
        return NutritionMacrosRecord.model_validate(record)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving macro record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving record: {str(e)}",
        )


@router.delete("/{record_id}",
    response_model=NutritionMacrosDeleteResponse,
    summary="Delete a macro record by ID",
    description="Delete a macro record by ID",
    responses={
        200: {"description": "Macro record deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Macro record not found"},
        500: {"description": "Internal server error"},
    }
)
async def delete_macro_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Delete a macro record by ID"""
    try:
        nutrition_service = NutritionService(db)
        record = nutrition_service.delete_macro_record(current_user.id, record_id)

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Record not found",
            )

        return NutritionMacrosDeleteResponse(
            message=f"Macro record {record_id} deleted successfully",
            deleted_count=1
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting macro record: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting macro record: {str(e)}",
        )


@router.get("/daily/{date}",
    response_model=DailyAggregation,
    summary="Get daily macro records",
    description="Get daily macro records",
    responses={
        200: {"description": "Daily macro records retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "No macro records found for the given date"},
        500: {"description": "Internal server error"},
    }
)
async def get_daily_macro_records(
    date: str,  # Format: YYYY-MM-DD
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Get all macro records for a specific day"""
    try:
        
        nutrition_service = NutritionService(db)
        data = nutrition_service.get_daily_macros_data(current_user.id, date)
        if not data.records:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No macro records found for the given date",
            )
        
        return DailyAggregation(
            date=date,
            total_calories=data.total_calories,
            total_protein=data.total_protein,
            total_carbs=data.total_carbs,
            total_fat=data.total_fat,
            meal_count=len(data.records),
            meals=[NutritionMacrosRecord.model_validate(record) for record in data.records],
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


@router.get("/aggregate",
    response_model=DailyAggregationResponse,
    summary="Get aggregated macro records by day",
    description="Get aggregated macro records by day",
    responses={
        200: {"description": "Aggregated macro records retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "No macro records found for the given date"},
        500: {"description": "Internal server error"},
    }
)
async def get_macro_aggregations(
    start_date: Optional[str] = None,  # Format: YYYY-MM-DD
    end_date: Optional[str] = None,  # Format: YYYY-MM-DD
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
):
    """Get aggregated macro records by day"""
    try:
        
        start_dt = None
        end_dt = None

        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            start_dt = datetime.combine(start_dt, datetime.min.time())
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            end_dt = datetime.combine(end_dt, datetime.max.time())


        nutrition_service = NutritionService(db)
        data = nutrition_service.get_macro_aggregations(current_user.id, start_dt, end_dt)

        if not data.records:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No macro records found",
            )

        # Group by date
        daily_groups = {}
        for record in data.records:
            date_key = record.datetime.date().strftime("%Y-%m-%d")
            if date_key not in daily_groups:
                daily_groups[date_key] = []
            daily_groups[date_key].append(record)

        # Create aggregations
        aggregations = []
        for date_str, day_records in daily_groups.items():
            total_calories = sum(record.calories for record in day_records if record.calories)
            total_protein = sum(record.protein for record in day_records if record.protein)
            total_carbs = sum(record.carbs for record in day_records if record.carbs)
            total_fat = sum(record.fat for record in day_records if record.fat)

            aggregations.append(
                DailyAggregation(
                    date=date_str,
                    total_calories=total_calories if total_calories > 0 else None,
                    total_protein=total_protein if total_protein > 0 else None,
                    total_carbs=total_carbs if total_carbs > 0 else None,
                    total_fat=total_fat if total_fat > 0 else None,
                    meal_count=len(day_records),
                    meals=[NutritionMacrosRecord.model_validate(record) for record in day_records],
                )
            )



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
