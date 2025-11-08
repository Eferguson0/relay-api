from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.nutrition.macros import NutritionMacros
from app.models.nutrition.foods import Food
from app.models.nutrition.consumption_logs import ConsumptionLog

# TODO: Reconcile transaction boundaries (commit/rollback) between services and repositories.
class NutritionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_macros_data(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, food_name: Optional[str] = None) -> List[NutritionMacros]:
        query = self.db.query(NutritionMacros).filter(NutritionMacros.user_id == user_id)
        if start_date:
            query = query.filter(NutritionMacros.datetime >= start_date)
        if end_date:
            query = query.filter(NutritionMacros.datetime <= end_date)
        if food_name:
            query = query.filter(NutritionMacros.food_name.ilike(f"%{food_name}%"))
        records = query.order_by(NutritionMacros.datetime.desc()).all()
        return records

    def create_macro_record(self, record: NutritionMacros) -> NutritionMacros:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update_macro_record(self, record: NutritionMacros) -> NutritionMacros:
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_macro_record_by_datetime_food(self, user_id: str, datetime: datetime, food_name: str) -> Optional[NutritionMacros]:
        return (
            self.db.query(NutritionMacros)
            .filter(
                NutritionMacros.user_id == user_id,
                NutritionMacros.datetime == datetime,
                NutritionMacros.food_name == food_name,
            )
            .one_or_none()
        )

    def get_macro_record_by_id(self, user_id: str, record_id: str) -> Optional[NutritionMacros]:
        return (
            self.db.query(NutritionMacros)
            .filter(
                NutritionMacros.id == record_id,
                NutritionMacros.user_id == user_id,
            )
            .one_or_none()
        )

    def delete_macro_record(self, user_id: str, record_id: str) -> Optional[NutritionMacros]:
        record = self.get_macro_record_by_id(user_id, record_id)
        if record:
            self.db.delete(record)
            self.db.commit()
        return None


    # Food helpers

    def list_foods(
        self,
        search: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Food]:
        query = self.db.query(Food)

        if search:
            query = query.filter(Food.name.ilike(f"%{search}%"))

        query = query.order_by(Food.name.asc())

        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        return query.all()

    def count_foods(self, search: Optional[str] = None) -> int:
        """Count total foods matching search criteria (before pagination)"""
        query = self.db.query(Food)
        if search:
            query = query.filter(Food.name.ilike(f"%{search}%"))
        return query.count()

    def get_food(self, food_id: str) -> Optional[Food]:
        return self.db.query(Food).filter(Food.id == food_id).one_or_none()

    def get_food_by_name(self, name: str) -> Optional[Food]:
        return self.db.query(Food).filter(Food.name == name).one_or_none()

    def create_food(self, food: Food) -> Food:
        self.db.add(food)
        self.db.commit()
        self.db.refresh(food)
        return food

    def update_food(self, food: Food) -> Food:
        self.db.commit()
        self.db.refresh(food)
        return food

    def delete_food(self, food: Food) -> None:
        self.db.delete(food)
        self.db.commit()


    # Consumption log helpers

    def count_consumption_logs(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> int:
        query = self.db.query(ConsumptionLog).filter(ConsumptionLog.user_id == user_id)
        if start_date:
            query = query.filter(ConsumptionLog.logged_at >= start_date)
        if end_date:
            query = query.filter(ConsumptionLog.logged_at <= end_date)
        return query.count()

    def list_consumption_logs(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[ConsumptionLog]:
        query = (
            self.db.query(ConsumptionLog)
            .options(joinedload(ConsumptionLog.food))
            .filter(ConsumptionLog.user_id == user_id)
        )

        if start_date:
            query = query.filter(ConsumptionLog.logged_at >= start_date)
        if end_date:
            query = query.filter(ConsumptionLog.logged_at <= end_date)

        query = query.order_by(ConsumptionLog.logged_at.desc())
        
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)
        
        return query.all()

    def get_consumption_log(self, user_id: str, log_id: str) -> Optional[ConsumptionLog]:
        return (
            self.db.query(ConsumptionLog)
            .options(joinedload(ConsumptionLog.food))
            .filter(
                ConsumptionLog.id == log_id,
                ConsumptionLog.user_id == user_id,
            )
            .one_or_none()
        )

    def create_consumption_log(self, log: ConsumptionLog) -> ConsumptionLog:
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def update_consumption_log(self, log: ConsumptionLog) -> ConsumptionLog:
        self.db.commit()
        self.db.refresh(log)
        return log

    def delete_consumption_log(self, log: ConsumptionLog) -> None:
        self.db.delete(log)
        self.db.commit()

    def get_consumption_log_macros_data(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, food_name: Optional[str] = None) -> List[ConsumptionLog]:
        query = self.db.query(ConsumptionLog).filter(ConsumptionLog.user_id == user_id)
        if start_date:
            query = query.filter(ConsumptionLog.logged_at >= start_date)
        if end_date:
            query = query.filter(ConsumptionLog.logged_at <= end_date)
        if food_name:
            query = query.join(Food).filter(Food.name.ilike(f"%{food_name}%"))
        records = query.order_by(ConsumptionLog.logged_at.desc()).all()
        return records
