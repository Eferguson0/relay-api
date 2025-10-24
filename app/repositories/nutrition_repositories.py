from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List   
from app.models.nutrition.macros import NutritionMacros

class NutritionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_macros_data(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None, meal_name: Optional[str] = None) -> List[NutritionMacros]:
        query = self.db.query(NutritionMacros).filter(NutritionMacros.user_id == user_id)
        if start_date:
            query = query.filter(NutritionMacros.datetime >= start_date)
        if end_date:
            query = query.filter(NutritionMacros.datetime <= end_date)
        if meal_name:
            query = query.filter(NutritionMacros.meal_name.ilike(f"%{meal_name}%"))
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

    def get_macro_record_by_datetime_meal(self, user_id: str, datetime: datetime, meal_name: str) -> Optional[NutritionMacros]:
        return (
            self.db.query(NutritionMacros)
            .filter(
                NutritionMacros.user_id == user_id,
                NutritionMacros.datetime == datetime,
                NutritionMacros.meal_name == meal_name,
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

        