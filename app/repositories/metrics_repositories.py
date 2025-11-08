from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List

from app.models.metric.activity.miles import ActivityMiles
from app.models.metric.activity.steps import ActivitySteps
from app.models.metric.activity.workouts import ActivityWorkouts
from app.models.metric.body.composition import BodyComposition
from app.models.metric.body.heartrate import BodyHeartRate
from app.models.metric.calories.active import CaloriesActive
from app.models.metric.calories.baseline import CaloriesBaseline
from app.models.metric.sleep.daily import SleepDaily
from app.models.enums import DataSource

# TODO: Reconcile transaction boundaries (commit/rollback) between services and repositories.
class MetricsRepository:
    def __init__(self, db: Session):
        self.db = db

# Body Composition Repository

    def get_body_composition_data(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[BodyComposition]:
        query = self.db.query(BodyComposition).filter(BodyComposition.user_id == user_id)
        if start_date:
            query = query.filter(BodyComposition.date_hour >= start_date)
        if end_date:
            query = query.filter(BodyComposition.date_hour <= end_date)
        return query.order_by(BodyComposition.date_hour.desc()).all()

    def get_body_composition_by_date_source(self, user_id: str, date_hour: datetime, source: DataSource) -> Optional[BodyComposition]:
        return (
            self.db.query(BodyComposition)
                .filter(
                    BodyComposition.user_id == user_id,
                    BodyComposition.date_hour == date_hour,
                    BodyComposition.source == source,
                )
                .one_or_none()
        )

    def create_body_composition_record(self, record: BodyComposition) -> BodyComposition:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update_body_composition_record(self, record: BodyComposition) -> BodyComposition:
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_body_composition_record(self, user_id: str, record_id: str) -> Optional[BodyComposition]:
        return (
            self.db.query(BodyComposition)
            .filter(
                BodyComposition.id == record_id,
                BodyComposition.user_id == user_id,
            )
            .one_or_none()
        )

    def delete_body_composition_record(self, user_id: str, record_id: str) -> Optional[BodyComposition]:
        record = self.get_body_composition_record(user_id, record_id)
        if record:
            self.db.delete(record)
            self.db.commit()
            return record
        return None

# Heart Rate Repository

    def get_heart_rate_data(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[BodyHeartRate]:
        query = self.db.query(BodyHeartRate).filter(BodyHeartRate.user_id == user_id)
        if start_date:
            query = query.filter(BodyHeartRate.date_hour >= start_date)
        if end_date:
            query = query.filter(BodyHeartRate.date_hour <= end_date)
        return query.order_by(BodyHeartRate.date_hour.desc()).all()

    def get_heart_rate_by_date_source(self, user_id: str, date_hour: datetime, source: DataSource) -> Optional[BodyHeartRate]:
        return (
            self.db.query(BodyHeartRate)
            .filter(
                BodyHeartRate.user_id == user_id,
                BodyHeartRate.date_hour == date_hour,
                BodyHeartRate.source == source,
            )
            .one_or_none()
        )

    def get_heart_rate_record(self, user_id: str, record_id: str) -> Optional[BodyHeartRate]:
        return (
            self.db.query(BodyHeartRate)
            .filter(
                BodyHeartRate.id == record_id,
                BodyHeartRate.user_id == user_id,
            )
            .one_or_none()
        )

    def create_heart_rate_record(self, record: BodyHeartRate) -> BodyHeartRate:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update_heart_rate_record(self, record: BodyHeartRate) -> BodyHeartRate:
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete_heart_rate_record(self, user_id: str, record_id: str) -> Optional[BodyHeartRate]:
        record = self.get_heart_rate_record(user_id, record_id)
        if record:
            self.db.delete(record)
            self.db.commit()
            return record
        return None

# Active Calories Repository

    def get_active_calories_data(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[CaloriesActive]:
        query = self.db.query(CaloriesActive).filter(CaloriesActive.user_id == user_id)
        if start_date:
            query = query.filter(CaloriesActive.date_hour >= start_date)
        if end_date:
            query = query.filter(CaloriesActive.date_hour <= end_date)
        return query.order_by(CaloriesActive.date_hour.desc()).all()

    def get_active_calories_by_date_source(self, user_id: str, date_hour: datetime, source: DataSource) -> Optional[CaloriesActive]:
        return (
            self.db.query(CaloriesActive)
            .filter(
                CaloriesActive.user_id == user_id,
                CaloriesActive.date_hour == date_hour,
                CaloriesActive.source == source,
            )
            .one_or_none()
        )

    def get_active_calories_record(self, user_id: str, record_id: str) -> Optional[CaloriesActive]:
        return (
            self.db.query(CaloriesActive)
            .filter(
                CaloriesActive.id == record_id,
                CaloriesActive.user_id == user_id,
            )
            .one_or_none()
        )

    def create_active_calories_record(self, record: CaloriesActive) -> CaloriesActive:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update_active_calories_record(self, record: CaloriesActive) -> CaloriesActive:
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete_active_calories_record(self, user_id: str, record_id: str) -> Optional[CaloriesActive]:
        record = self.get_active_calories_record(user_id, record_id)
        if record:
            self.db.delete(record)
            self.db.commit()
            return record
        return None

# Baseline Calories Repository

    def get_baseline_calories_data(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[CaloriesBaseline]:
        query = self.db.query(CaloriesBaseline).filter(CaloriesBaseline.user_id == user_id)
        if start_date:
            query = query.filter(CaloriesBaseline.date_hour >= start_date)
        if end_date:
            query = query.filter(CaloriesBaseline.date_hour <= end_date)
        return query.order_by(CaloriesBaseline.date_hour.desc()).all()

    def get_baseline_calories_by_date_source(self, user_id: str, date_hour: datetime, source: DataSource) -> Optional[CaloriesBaseline]:
        return (
            self.db.query(CaloriesBaseline)
            .filter(
                CaloriesBaseline.user_id == user_id,
                CaloriesBaseline.date_hour == date_hour,
                CaloriesBaseline.source == source,
            )
            .one_or_none()
        )

    def get_baseline_calories_record(self, user_id: str, record_id: str) -> Optional[CaloriesBaseline]:
        return (
            self.db.query(CaloriesBaseline)
            .filter(
                CaloriesBaseline.id == record_id,
                CaloriesBaseline.user_id == user_id,
            )
            .one_or_none()
        )

    def create_baseline_calories_record(self, record: CaloriesBaseline) -> CaloriesBaseline:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update_baseline_calories_record(self, record: CaloriesBaseline) -> CaloriesBaseline:
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete_baseline_calories_record(self, user_id: str, record_id: str) -> Optional[CaloriesBaseline]:
        record = self.get_baseline_calories_record(user_id, record_id)
        if record:
            self.db.delete(record)
            self.db.commit()
            return record
        return None

# Sleep Daily Repository

    def get_sleep_daily_data(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[SleepDaily]:
        query = self.db.query(SleepDaily).filter(SleepDaily.user_id == user_id)
        if start_date:
            query = query.filter(SleepDaily.date_day >= start_date)
        if end_date:
            query = query.filter(SleepDaily.date_day <= end_date)
        return query.order_by(SleepDaily.date_day.desc()).all()

    def get_sleep_daily_by_date_source(self, user_id: str, date_day: datetime, source: DataSource) -> Optional[SleepDaily]:
        return (
            self.db.query(SleepDaily)
            .filter(
                SleepDaily.user_id == user_id,
                SleepDaily.date_day == date_day,
                SleepDaily.source == source,
            )
            .one_or_none()
        )

    def get_sleep_daily_record(self, user_id: str, record_id: str) -> Optional[SleepDaily]:
        return (
            self.db.query(SleepDaily)
            .filter(
                SleepDaily.id == record_id,
                SleepDaily.user_id == user_id,
            )
            .one_or_none()
        )

    def create_sleep_daily_record(self, record: SleepDaily) -> SleepDaily:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update_sleep_daily_record(self, record: SleepDaily) -> SleepDaily:
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete_sleep_daily_record(self, user_id: str, record_id: str) -> Optional[SleepDaily]:
        record = self.get_sleep_daily_record(user_id, record_id)
        if record:
            self.db.delete(record)
            self.db.commit()
            return record
        return None

# Miles Repository

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
        return self.db.query(ActivityMiles).filter(ActivityMiles.user_id == user_id, ActivityMiles.date_hour == date_hour, ActivityMiles.source == source).first()

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

# Steps Repository

    def get_steps_data(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[ActivitySteps]:
        query = self.db.query(ActivitySteps).filter(ActivitySteps.user_id == user_id)
        if start_date:
            query = query.filter(ActivitySteps.date_hour >= start_date)
        if end_date:
            query = query.filter(ActivitySteps.date_hour <= end_date)
        records = query.order_by(ActivitySteps.date_hour.desc()).all()
        return records

    def get_steps_data_by_date_hour_source(self, user_id: str, date_hour: datetime, source: str) -> Optional[ActivitySteps]:
        return self.db.query(ActivitySteps).filter(ActivitySteps.user_id == user_id, ActivitySteps.date_hour == date_hour, ActivitySteps.source == source).first()

    def update_steps_record(self, record: ActivitySteps) -> ActivitySteps:
        self.db.commit()
        self.db.refresh(record)
        return record

    def create_new_steps_record(self, record: ActivitySteps) -> ActivitySteps:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_steps_data_by_id(self, user_id: str, record_id: str) -> Optional[ActivitySteps]:
        return self.db.query(ActivitySteps).filter(ActivitySteps.id == record_id, ActivitySteps.user_id == user_id).first()

    def delete_steps_record(self, user_id: str, record_id: str) -> Optional[ActivitySteps]:
        record = self.db.query(ActivitySteps).filter(ActivitySteps.id == record_id, ActivitySteps.user_id == user_id).first()
        if record:
            self.db.delete(record)
            self.db.commit()
            return record
        return None


# Workouts Repository

    def get_workouts_data(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[ActivityWorkouts]:
        query = self.db.query(ActivityWorkouts).filter(ActivityWorkouts.user_id == user_id)
        if start_date:
            query = query.filter(ActivityWorkouts.date >= start_date)
        if end_date:
            query = query.filter(ActivityWorkouts.date <= end_date)
        records = query.order_by(ActivityWorkouts.date.desc()).all()
        return records

    def get_workouts_data_by_id(self, user_id: str, record_id: str) -> Optional[ActivityWorkouts]:
        return self.db.query(ActivityWorkouts).filter(ActivityWorkouts.id == record_id, ActivityWorkouts.user_id == user_id).first()

    def get_workouts_data_by_date_source(self, user_id: str, date: datetime, source: str) -> Optional[ActivityWorkouts]:
        return self.db.query(ActivityWorkouts).filter(ActivityWorkouts.user_id == user_id, ActivityWorkouts.date == date, ActivityWorkouts.source == source).first()

    def update_workouts_record(self, record: ActivityWorkouts) -> ActivityWorkouts:
        self.db.commit()
        self.db.refresh(record)
        return record

    def create_new_workouts_record(self, record: ActivityWorkouts) -> ActivityWorkouts:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete_workouts_record(self, user_id: str, record_id: str) -> Optional[ActivityWorkouts]:
        record = self.db.query(ActivityWorkouts).filter(ActivityWorkouts.id == record_id, ActivityWorkouts.user_id == user_id).first()
        if record:
            self.db.delete(record)
            self.db.commit()
            return record
        return None
