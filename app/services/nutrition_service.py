import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.rid import generate_rid
from app.core.datetime_utils import parse_iso_datetime, get_day_boundaries_from_datetime
from app.models.nutrition.macros import NutritionMacros
from app.models.nutrition.foods import Food
from app.models.nutrition.consumption_logs import ConsumptionLog
from app.schemas.nutrition.foods import FoodCreate, FoodUpdate
from app.schemas.nutrition.consumption_logs import (
    ConsumptionLogCreate,
    ConsumptionLogUpdate,
    DailyConsumptionAggregation,
)
from app.schemas.nutrition.macros import (
    DailyAggregation,
    NutritionMacrosBulkCreate,
    NutritionMacrosRecord,
    NutritionMacrosRecordCreate,
)
from app.repositories.nutrition_repositories import NutritionRepository

logger = logging.getLogger(__name__)

@dataclass
class NutritionMacrosExport:
    records: List[NutritionMacros]
    total_count: int
    total_calories: float
    total_protein: Optional[float] = None
    total_carbs: Optional[float] = None
    total_fat: Optional[float] = None

@dataclass
class ConsumptionLogExport:
    records: List[ConsumptionLog]
    total_count: int
    total_calories: float
    total_protein: Optional[float] = None
    total_carbs: Optional[float] = None
    total_fat: Optional[float] = None

class NutritionService:
    def __init__(self, db: Session):
        self.db = db

    # Food operations
    def list_foods(
        self,
        search: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> tuple[List[Food], int]:
        """Returns (foods_list, total_count) - API layer constructs response"""
        repository = NutritionRepository(self.db)
        # Get total count before pagination
        total_count = repository.count_foods(search=search)
        # Get paginated results
        foods = repository.list_foods(search=search, limit=limit, offset=offset)
        return foods, total_count

    def create_food(self, food_data: FoodCreate) -> Food:
        repository = NutritionRepository(self.db)
        food = Food(
            id=generate_rid("nutrition", "food"),
            name=food_data.name,
            brand=food_data.brand,
            calories=food_data.calories,
            protein=food_data.protein,
            carbs=food_data.carbs,
            fat=food_data.fat,
            serving_unit=food_data.serving_unit or "serving",
            serving_size=food_data.serving_size if food_data.serving_size is not None else 1.0,
        )
        repository.create_food(food)
        return food

    def get_food(self, food_id: str) -> Optional[Food]:
        repository = NutritionRepository(self.db)
        return repository.get_food(food_id)

    def update_food(
        self,
        food: Food,
        food_data: FoodUpdate,
    ) -> Food:
        repository = NutritionRepository(self.db)
        
        # Only update fields that are provided (not None)
        if food_data.name is not None:
            food.name = food_data.name
        if food_data.brand is not None:
            food.brand = food_data.brand
        if food_data.calories is not None:
            food.calories = food_data.calories
        if food_data.protein is not None:
            food.protein = food_data.protein
        if food_data.carbs is not None:
            food.carbs = food_data.carbs
        if food_data.fat is not None:
            food.fat = food_data.fat
        if food_data.serving_unit is not None:
            food.serving_unit = food_data.serving_unit
        if food_data.serving_size is not None:
            food.serving_size = food_data.serving_size
        
        repository.update_food(food)
        return food

    def delete_food(self, food: Food) -> None:
        repository = NutritionRepository(self.db)
        repository.delete_food(food)


    # Consumption log operations

    def list_consumption_logs(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> tuple[List[ConsumptionLog], int]:
        """Returns (logs_list, total_count) - API layer constructs response"""
        repository = NutritionRepository(self.db)
        # Get total count before pagination
        total_count = repository.count_consumption_logs(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
        )
        # Get paginated results
        logs = repository.list_consumption_logs(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )
        return logs, total_count

    def create_consumption_log(
        self,
        user_id: str,
        log_data: ConsumptionLogCreate,
    ) -> ConsumptionLog:
        repository = NutritionRepository(self.db)
        
        # Validate that the food exists
        food = repository.get_food(log_data.food_id)
        if not food:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Food with id {log_data.food_id} not found"
            )
        
        log_logged_at = parse_iso_datetime(log_data.logged_at)
        log = ConsumptionLog(
            id=generate_rid("nutrition", "consumption_log"),
            user_id=user_id,
            logged_at=log_logged_at,
            food_id=log_data.food_id,
            servings=log_data.servings,  # Has default in schema, so should always have a value
            serving_unit=log_data.serving_unit or "serving",
            calories_total=log_data.calories_total,
            protein_total=log_data.protein_total,
            carbs_total=log_data.carbs_total,
            fat_total=log_data.fat_total,
            is_saved=log_data.is_saved,  # Has default in schema, so should always have a value
        )
        repository.create_consumption_log(log)
        return log

    def get_consumption_log(self, user_id: str, log_id: str) -> Optional[ConsumptionLog]:
        repository = NutritionRepository(self.db)
        return repository.get_consumption_log(user_id, log_id)

    def update_consumption_log(
        self,
        log: ConsumptionLog,
        log_data: ConsumptionLogUpdate,
    ) -> ConsumptionLog:
        repository = NutritionRepository(self.db)
        
        # Only update fields that are provided (not None)
        # Note: food_id cannot be updated - it's the source reference to what was consumed
        if log_data.logged_at is not None:
            log.logged_at = parse_iso_datetime(log_data.logged_at)
        if log_data.servings is not None:
            log.servings = log_data.servings
        if log_data.serving_unit is not None:
            log.serving_unit = log_data.serving_unit
        if log_data.calories_total is not None:
            log.calories_total = log_data.calories_total
        if log_data.protein_total is not None:
            log.protein_total = log_data.protein_total
        if log_data.carbs_total is not None:
            log.carbs_total = log_data.carbs_total
        if log_data.fat_total is not None:
            log.fat_total = log_data.fat_total
        if log_data.is_saved is not None:
            log.is_saved = log_data.is_saved
        
        repository.update_consumption_log(log)
        return log

    def delete_consumption_log(self, log: ConsumptionLog) -> None:
        repository = NutritionRepository(self.db)
        repository.delete_consumption_log(log)

    def get_daily_consumption_logs_data(self, user_id: str, date: str) -> ConsumptionLogExport:
        nutrition_repository = NutritionRepository(self.db)
        
        # Parse the date and get UTC day boundaries
        start_datetime, end_datetime = get_day_boundaries_from_datetime(date)
        
        records = nutrition_repository.get_consumption_log_macros_data(user_id, start_datetime, end_datetime, None)

        total_calories, total_protein, total_carbs, total_fat = self._calculate_consumption_totals(records)

        return ConsumptionLogExport(
            records=records,
            total_count=len(records),
            total_calories=total_calories,  # Required field, can be 0.0
            total_protein=total_protein if total_protein > 0 else None,
            total_carbs=total_carbs if total_carbs > 0 else None,
            total_fat=total_fat if total_fat > 0 else None,
        )

    def _calculate_consumption_totals(self, records: List[ConsumptionLog]) -> tuple:
        """Helper method to calculate totals from consumption log records"""
        total_calories = 0.0
        total_protein = 0.0
        total_carbs = 0.0
        total_fat = 0.0

        for record in records:
            total_calories += float(record.calories_total)
            if record.protein_total is not None:
                total_protein += float(record.protein_total)
            if record.carbs_total is not None:
                total_carbs += float(record.carbs_total)
            if record.fat_total is not None:
                total_fat += float(record.fat_total)

        return total_calories, total_protein, total_carbs, total_fat


    # Macro operations
    def get_macros_export_data(
        self, 
        user_id: str, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None, 
        food_name: Optional[str] = None
    ) -> NutritionMacrosExport:

        nutrition_repository = NutritionRepository(self.db)
        records = nutrition_repository.get_macros_data(user_id, start_date, end_date, food_name)
        
        total_calories, total_protein, total_carbs, total_fat = self._calculate_totals(records)


        return NutritionMacrosExport(
            records=records,
            total_count=len(records),
            total_calories=total_calories,  # Required field, can be 0.0
            total_protein=total_protein if total_protein > 0 else None,
            total_carbs=total_carbs if total_carbs > 0 else None,
            total_fat=total_fat if total_fat > 0 else None,
        )


    def get_daily_macros_data(self, user_id: str, date: str) -> NutritionMacrosExport:
        nutrition_repository = NutritionRepository(self.db)
        
        # Parse the date and get UTC day boundaries
        start_datetime, end_datetime = get_day_boundaries_from_datetime(date)
        
        records = nutrition_repository.get_macros_data(user_id, start_datetime, end_datetime, None)


        total_calories, total_protein, total_carbs, total_fat = self._calculate_totals(records)


        return NutritionMacrosExport(
            records=records,
            total_count=len(records),
            total_calories=total_calories,  # Required field, can be 0.0
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
            record_datetime = parse_iso_datetime(record_data.datetime)
            existing_record = nutrition_repository.get_macro_record_by_datetime_food(user_id, record_datetime, record_data.food_name)
            if existing_record:
                # Update existing record
                setattr(existing_record, "calories", record_data.calories)  # Required field, always set
                if record_data.protein is not None:
                    setattr(existing_record, "protein", record_data.protein)
                if record_data.carbs is not None:
                    setattr(existing_record, "carbs", record_data.carbs)
                if record_data.fat is not None:
                    setattr(existing_record, "fat", record_data.fat)
                if record_data.notes is not None:
                    setattr(existing_record, "notes", record_data.notes)
                setattr(existing_record, "is_saved", record_data.is_saved)
                setattr(existing_record, "updated_at", datetime.now(timezone.utc))
                updated_record = nutrition_repository.update_macro_record(existing_record)
                processed_records.append(updated_record)
                updated_count += 1
            else:
                # Create new macro record
                new_record = NutritionMacros(
                    id=generate_rid("nutrition", "macros"),
                    user_id=user_id,
                    datetime=record_datetime,
                    food_name=record_data.food_name,
                    calories=record_data.calories,
                    protein=record_data.protein,
                    carbs=record_data.carbs,
                    fat=record_data.fat,
                    notes=record_data.notes,
                    is_saved=record_data.is_saved,
                )
                nutrition_repository.create_macro_record(new_record)
                processed_records.append(new_record)
                created_count += 1


        return processed_records, created_count, updated_count

    def create_macro_record(self, record_data: NutritionMacrosRecordCreate, user_id: str) -> NutritionMacros:
        nutrition_repository = NutritionRepository(self.db)

        record_datetime = parse_iso_datetime(record_data.datetime)
        # Create new macro record
        new_record = NutritionMacros(
            id=generate_rid("nutrition", "macros"),
            user_id=user_id,
            datetime=record_datetime,
            food_name=record_data.food_name,
            calories=record_data.calories,
            protein=record_data.protein,
            carbs=record_data.carbs,
            fat=record_data.fat,
            is_saved=record_data.is_saved,
            notes=record_data.notes,
        )
        nutrition_repository.create_macro_record(new_record)
        return new_record

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
        total_calories, total_protein, total_carbs, total_fat = self._calculate_totals(records)
        return NutritionMacrosExport(
            records=records,
            total_count=len(records),
            total_calories=total_calories,  # Required field, can be 0.0
            total_protein=total_protein if total_protein > 0 else None,
            total_carbs=total_carbs if total_carbs > 0 else None,
            total_fat=total_fat if total_fat > 0 else None,
        )
