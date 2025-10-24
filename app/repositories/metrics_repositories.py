from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from app.models.metric.activity.miles import ActivityMiles

class MetricsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_miles_data(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[ActivityMiles]:
        query = self.db.query(ActivityMiles).filter(ActivityMiles.user_id == user_id)
        if start_date:
            query = query.filter(ActivityMiles.date_hour >= start_date)
        if end_date:
            query = query.filter(ActivityMiles.date_hour <= end_date)
        records = query.order_by(ActivityMiles.date_hour.desc()).all()
        return records

    def get_miles_data_by_id(self, user_id: str, record_id: str) -> ActivityMiles:
        return self.db.query(ActivityMiles).filter(ActivityMiles.id == record_id, ActivityMiles.user_id == user_id).first()

    def get_miles_data_by_date_hour_source(self, user_id: str, date_hour: datetime, source: str) -> Optional[ActivityMiles]:
        return self.db.query(ActivityMiles).filter(ActivityMiles.user_id == user_id, ActivityMiles.date_hour == date_hour, ActivityMiles.source == source).all()

    def create_new_miles_record(self, record: ActivityMiles) -> ActivityMiles:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update_miles_record(self, record: ActivityMiles) -> ActivityMiles:
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete_miles_record(self, user_id: str, record_id: str) -> Optional[ActivityMiles]:
        record = self.db.query(ActivityMiles).filter(ActivityMiles.id == record_id, ActivityMiles.user_id == user_id).first()
        if record:
            self.db.delete(record)
            self.db.commit()
            return record
        return None
