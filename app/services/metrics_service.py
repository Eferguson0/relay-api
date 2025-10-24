import logging
from datetime import datetime
from typing import Optional, List


from sqlalchemy.orm import Session

from app.models.metric.activity.miles import ActivityMiles
from app.models.metric.body.composition import BodyComposition
from app.models.metric.body.heartrate import BodyHeartRate
from app.models.metric.calories.active import CaloriesActive
from app.models.metric.calories.baseline import CaloriesBaseline
from app.models.metric.sleep.daily import SleepDaily
from app.repositories.metrics_repositories import MetricsRepository
from app.schemas.metric.activity.miles import ActivityMilesBulkCreate
from app.core.rid import generate_rid

logger = logging.getLogger(__name__)

class MetricsService:
    def __init__(self, db: Session):
        self.db = db

# Miles Services

    def get_miles_data(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[ActivityMiles]:
        """Get activity miles data with optional date filtering"""
        metrics_repository = MetricsRepository(self.db)
        records = metrics_repository.get_miles_data(user_id, start_date, end_date)
        return records

    def get_miles_data_by_id(self, user_id: str, record_id: str) -> Optional[ActivityMiles]:
        """Get a specific activity miles record by ID"""
        metrics_repository = MetricsRepository(self.db)
        record = metrics_repository.get_miles_data_by_id(user_id, record_id)
        return record

    def create_or_update_multiple_miles_records(self, bulk_data: ActivityMilesBulkCreate, user_id: str) -> tuple:
        """Create or update multiple activity miles records (bulk upsert)"""
        
        created_count = 0
        updated_count = 0
        processed_records = []
        
        metrics_repository = MetricsRepository(self.db)
        
        for miles_data in bulk_data.records:
            existing_record = metrics_repository.get_miles_data_by_date_hour_source(user_id, miles_data.date_hour, miles_data.source)
            
            if existing_record:
                # Update existing record
                if miles_data.miles is not None:
                    setattr(existing_record, "miles", miles_data.miles)
                if miles_data.activity_type is not None:
                    setattr(existing_record, "activity_type", miles_data.activity_type)
                setattr(existing_record, "updated_at", datetime.utcnow())
                updated_record = metrics_repository.update_miles_record(existing_record)
                processed_records.append(updated_record)
                updated_count += 1
            else:
                # Create new activity miles record
                new_record = ActivityMiles(
                    id=generate_rid("metric", "activity_miles"),
                    user_id=user_id,
                    date_hour=miles_data.date_hour,
                    miles=miles_data.miles,
                    activity_type=miles_data.activity_type,
                    source=miles_data.source,
                )
                new_record = metrics_repository.create_new_miles_record(new_record)
                processed_records.append(new_record)
                created_count += 1        
        
        return processed_records, created_count, updated_count

    def delete_miles_record(self, user_id: str, record_id: str) -> Optional[ActivityMiles]:
        """Delete an activity miles record"""
        metrics_repository = MetricsRepository(self.db)
        record = metrics_repository.delete_miles_record(user_id, record_id)
        return record