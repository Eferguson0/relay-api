from typing import List, Optional
from datetime import datetime
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.models.nutrition.macros import NutritionMacros
from app.schemas.nutrition.macros import (
    DailyAggregation,
    NutritionMacrosRecord,
    NutritionMacrosBulkCreate,
)
from app.repositories.nutrition_repositories import NutritionRepository
import logging

logger = logging.getLogger(__name__)

@dataclass
class NutritionMacrosExport:
    records: List[NutritionMacros]
    total_count: int
    total_calories: Optional[float] = None
    total_protein: Optional[float] = None
    total_carbs: Optional[float] = None
    total_fat: Optional[float] = None

class NutritionService:
    def __init__(self, db: Session):
        self.db = db

    def get_macros_export_data(
        self, 
        user_id: str, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None, 
        meal_name: Optional[str] = None
    ) -> NutritionMacrosExport:

        nutrition_repository = NutritionRepository(self.db)
        records = nutrition_repository.get_macros_data(user_id, start_date, end_date, meal_name)
        
        total_calories, total_protein, total_carbs, total_fat = self._calculate_totals(records)


        return NutritionMacrosExport(
            records=records,
            total_count=len(records),
            total_calories=total_calories if total_calories > 0 else None,
            total_protein=total_protein if total_protein > 0 else None,
            total_carbs=total_carbs if total_carbs > 0 else None,
            total_fat=total_fat if total_fat > 0 else None,
        )


    def get_daily_macros_data(self, user_id: str, date: str) -> NutritionMacrosExport:
        nutrition_repository = NutritionRepository(self.db)
        
        # Parse the date
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())
        
        records = nutrition_repository.get_macros_data(user_id, start_datetime, end_datetime, None)


        total_calories, total_protein, total_carbs, total_fat = self._calculate_totals(records)


        return NutritionMacrosExport(
            records=records,
            total_count=len(records),
            total_calories=total_calories if total_calories > 0 else None,
            total_protein=total_protein if total_protein > 0 else None,
            total_carbs=total_carbs if total_carbs > 0 else None,
            total_fat=total_fat if total_fat > 0 else None,
        )



    def _calculate_totals(self, records: List[NutritionMacros]) -> tuple:
        """Helper method to calculate totals from nutrition records"""
        total_calories = 0.0
        total_protein = 0.0
        total_carbs = 0.0
        total_fat = 0.0

        for record in records:
            if record.calories is not None:
                total_calories += float(record.calories)
            if record.protein is not None:
                total_protein += float(record.protein)
            if record.carbs is not None:
                total_carbs += float(record.carbs)
            if record.fat is not None:
                total_fat += float(record.fat)

        return total_calories, total_protein, total_carbs, total_fat

    def create_or_update_multiple_macro_records(self, bulk_data: NutritionMacrosBulkCreate, user_id: str) -> tuple:
        nutrition_repository = NutritionRepository(self.db)

        created_count = 0
        updated_count = 0
        processed_records = []

        for record_data in bulk_data.records:
            existing_record = nutrition_repository.get_macro_record_by_datetime_meal(user_id, record_data.datetime, record_data.meal_name)
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
                updated_record = nutrition_repository.update_macro_record(existing_record)
                processed_records.append(updated_record)
                updated_count += 1
            else:
                # Create new macro record
                new_record = NutritionMacros(
                    id=generate_rid("nutrition", "macros"),
                    user_id=user_id,
                    datetime=record_data.datetime,
                    protein=record_data.protein,
                    carbs=record_data.carbs,
                    fat=record_data.fat,
                    calories=record_data.calories,
                    meal_name=record_data.meal_name,
                    notes=record_data.notes,
                )
                nutrition_repository.create_macro_record(new_record)
                processed_records.append(new_record)
                created_count += 1


        return processed_records, created_count, updated_count

    def get_macro_record(self, user_id: str, record_id: str) -> Optional[NutritionMacros]:
        nutrition_repository = NutritionRepository(self.db)
        return nutrition_repository.get_macro_record_by_id(user_id, record_id)


    def delete_macro_record(self, user_id: str, record_id: str) -> Optional[NutritionMacros]:
        nutrition_repository = NutritionRepository(self.db)
        deleted_record = nutrition_repository.delete_macro_record(user_id, record_id)
        logger.info(f"Deleted macro record {record_id} for user {user_id}")
        return deleted_record


    def get_macro_aggregations(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> NutritionMacrosExport:
        nutrition_repository = NutritionRepository(self.db)
        records = nutrition_repository.get_macros_data(user_id, start_date, end_date, None)
        return NutritionMacrosExport(
            records=records,
            total_count=len(records),
            total_calories=None,
            total_protein=None,
            total_carbs=None,
            total_fat=None,
        )