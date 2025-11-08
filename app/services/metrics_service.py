from datetime import datetime, timezone
from typing import Optional, List


from sqlalchemy.orm import Session

from app.models.metric.activity.miles import ActivityMiles
from app.models.metric.activity.steps import ActivitySteps
from app.models.metric.activity.workouts import ActivityWorkouts
from app.models.metric.body.composition import BodyComposition
from app.models.metric.body.heartrate import BodyHeartRate
from app.models.metric.calories.active import CaloriesActive
from app.models.metric.calories.baseline import CaloriesBaseline
from app.models.metric.sleep.daily import SleepDaily
from app.models.enums import DataSource
from app.repositories.metrics_repositories import MetricsRepository
from app.schemas.metric.activity.miles import ActivityMilesBulkCreate
from app.schemas.metric.activity.steps import ActivityStepsBulkCreate
from app.schemas.metric.activity.workouts import ActivityWorkoutsBulkCreate
from app.schemas.metric.body.composition import BodyCompositionBulkCreate
from app.schemas.metric.body.heartrate import HeartRateBulkCreate
from app.schemas.metric.calories.active import CaloriesActiveBulkCreate
from app.schemas.metric.calories.baseline import CaloriesBaselineBulkCreate
from app.schemas.metric.sleep.daily import SleepDailyBulkCreate
from app.core.rid import generate_rid


class MetricsService:
    def __init__(self, db: Session):
        self.db = db

# Body Composition Services

    def get_body_composition_data(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[BodyComposition]:
        """Get body composition data with optional date filtering"""
        metrics_repository = MetricsRepository(self.db)
        return metrics_repository.get_body_composition_data(user_id, start_date, end_date)

    def create_or_update_multiple_body_composition_records(self, bulk_data: BodyCompositionBulkCreate, user_id: str) -> tuple:
        """Create or update multiple body composition records (bulk upsert)"""

        created_count = 0
        updated_count = 0
        processed_records = []

        metrics_repository = MetricsRepository(self.db)

        for composition_data in bulk_data.records:
            data_source = composition_data.source or DataSource.MANUAL
            existing_record = metrics_repository.get_body_composition_by_date_source(
                user_id=user_id,
                date_hour=composition_data.measurement_date,
                source=data_source,
            )

            if existing_record:
                if composition_data.weight is not None:
                    existing_record.weight = composition_data.weight
                if composition_data.body_fat_percentage is not None:
                    existing_record.body_fat_percentage = composition_data.body_fat_percentage
                if composition_data.muscle_mass_percentage is not None:
                    existing_record.muscle_mass_percentage = composition_data.muscle_mass_percentage
                if composition_data.bone_density is not None:
                    existing_record.bone_density = composition_data.bone_density
                if composition_data.water_percentage is not None:
                    existing_record.water_percentage = composition_data.water_percentage
                if composition_data.visceral_fat is not None:
                    existing_record.visceral_fat = composition_data.visceral_fat
                if composition_data.bmr is not None:
                    existing_record.bmr = composition_data.bmr
                if composition_data.measurement_method is not None:
                    existing_record.measurement_method = composition_data.measurement_method
                if composition_data.notes is not None:
                    existing_record.notes = composition_data.notes
                existing_record.updated_at = datetime.now(timezone.utc)
                updated_record = metrics_repository.update_body_composition_record(existing_record)
                processed_records.append(updated_record)
                updated_count += 1
            else:
                new_record = BodyComposition(
                    id=generate_rid("metric", "body_composition"),
                    user_id=user_id,
                    date_hour=composition_data.measurement_date,
                    source=data_source,
                    weight=composition_data.weight,
                    body_fat_percentage=composition_data.body_fat_percentage,
                    muscle_mass_percentage=composition_data.muscle_mass_percentage,
                    bone_density=composition_data.bone_density,
                    water_percentage=composition_data.water_percentage,
                    visceral_fat=composition_data.visceral_fat,
                    bmr=composition_data.bmr,
                    measurement_method=composition_data.measurement_method,
                    notes=composition_data.notes,
                )
                new_record = metrics_repository.create_body_composition_record(new_record)
                processed_records.append(new_record)
                created_count += 1

        return processed_records, created_count, updated_count

    def delete_body_composition_record(self, user_id: str, record_id: str) -> Optional[BodyComposition]:
        """Delete a body composition record"""
        metrics_repository = MetricsRepository(self.db)
        return metrics_repository.delete_body_composition_record(user_id, record_id)

# Heart Rate Services

    def get_heart_rate_data(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[BodyHeartRate]:
        """Get heart rate data with optional date filtering"""
        metrics_repository = MetricsRepository(self.db)
        return metrics_repository.get_heart_rate_data(user_id, start_date, end_date)

    def create_or_update_multiple_heart_rate_records(self, bulk_data: HeartRateBulkCreate, user_id: str) -> tuple:
        """Create or update multiple heart rate records (bulk upsert)"""

        created_count = 0
        updated_count = 0
        processed_records = []

        metrics_repository = MetricsRepository(self.db)

        for heart_rate_data in bulk_data.records:
            data_source = (
                heart_rate_data.source
                if isinstance(heart_rate_data.source, DataSource)
                else DataSource(heart_rate_data.source)
            )
            existing_record = metrics_repository.get_heart_rate_by_date_source(
                user_id=user_id,
                date_hour=heart_rate_data.date_hour,
                source=data_source,
            )

            if existing_record:
                if heart_rate_data.heart_rate is not None:
                    existing_record.heart_rate = heart_rate_data.heart_rate
                if heart_rate_data.avg_hr is not None:
                    existing_record.avg_hr = heart_rate_data.avg_hr
                if heart_rate_data.max_hr is not None:
                    existing_record.max_hr = heart_rate_data.max_hr
                if heart_rate_data.min_hr is not None:
                    existing_record.min_hr = heart_rate_data.min_hr
                if heart_rate_data.resting_hr is not None:
                    existing_record.resting_hr = heart_rate_data.resting_hr
                if heart_rate_data.heart_rate_variability is not None:
                    existing_record.heart_rate_variability = heart_rate_data.heart_rate_variability
                existing_record.updated_at = datetime.now(timezone.utc)
                updated_record = metrics_repository.update_heart_rate_record(existing_record)
                processed_records.append(updated_record)
                updated_count += 1
            else:
                new_record = BodyHeartRate(
                    id=generate_rid("metric", "body_heartrate"),
                    user_id=user_id,
                    date_hour=heart_rate_data.date_hour,
                    heart_rate=heart_rate_data.heart_rate,
                    min_hr=heart_rate_data.min_hr,
                    avg_hr=heart_rate_data.avg_hr,
                    max_hr=heart_rate_data.max_hr,
                    resting_hr=heart_rate_data.resting_hr,
                    heart_rate_variability=heart_rate_data.heart_rate_variability,
                    source=data_source,
                )
                new_record = metrics_repository.create_heart_rate_record(new_record)
                processed_records.append(new_record)
                created_count += 1

        return processed_records, created_count, updated_count

    def get_heart_rate_record(self, user_id: str, record_id: str) -> Optional[BodyHeartRate]:
        """Get a specific heart rate record by ID"""
        metrics_repository = MetricsRepository(self.db)
        return metrics_repository.get_heart_rate_record(user_id, record_id)

    def delete_heart_rate_record(self, user_id: str, record_id: str) -> Optional[BodyHeartRate]:
        """Delete a heart rate record"""
        metrics_repository = MetricsRepository(self.db)
        return metrics_repository.delete_heart_rate_record(user_id, record_id)

# Active Calories Services

    def get_active_calories_data(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[CaloriesActive]:
        """Get active calories data with optional date filtering"""
        metrics_repository = MetricsRepository(self.db)
        return metrics_repository.get_active_calories_data(user_id, start_date, end_date)

    def create_or_update_multiple_active_calories_records(self, bulk_data: CaloriesActiveBulkCreate, user_id: str) -> tuple:
        """Create or update multiple active calories records (bulk upsert)"""

        created_count = 0
        updated_count = 0
        processed_records = []

        metrics_repository = MetricsRepository(self.db)

        for calories_data in bulk_data.records:
            data_source = calories_data.source
            existing_record = metrics_repository.get_active_calories_by_date_source(
                user_id=user_id,
                date_hour=calories_data.date_hour,
                source=data_source,
            )

            if existing_record:
                if calories_data.calories_burned is not None:
                    existing_record.calories_burned = calories_data.calories_burned
                existing_record.updated_at = datetime.now(timezone.utc)
                updated_record = metrics_repository.update_active_calories_record(existing_record)
                processed_records.append(updated_record)
                updated_count += 1
            else:
                new_record = CaloriesActive(
                    id=generate_rid("metric", "active_calories"),
                    user_id=user_id,
                    date_hour=calories_data.date_hour,
                    calories_burned=calories_data.calories_burned,
                    source=data_source,
                )
                new_record = metrics_repository.create_active_calories_record(new_record)
                processed_records.append(new_record)
                created_count += 1

        return processed_records, created_count, updated_count

    def get_active_calories_record(self, user_id: str, record_id: str) -> Optional[CaloriesActive]:
        """Get a specific active calories record by ID"""
        metrics_repository = MetricsRepository(self.db)
        return metrics_repository.get_active_calories_record(user_id, record_id)

    def delete_active_calories_record(self, user_id: str, record_id: str) -> Optional[CaloriesActive]:
        """Delete an active calories record"""
        metrics_repository = MetricsRepository(self.db)
        return metrics_repository.delete_active_calories_record(user_id, record_id)

# Baseline Calories Services

    def get_baseline_calories_data(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[CaloriesBaseline]:
        """Get baseline calories data with optional date filtering"""
        metrics_repository = MetricsRepository(self.db)
        return metrics_repository.get_baseline_calories_data(user_id, start_date, end_date)

    def create_or_update_multiple_baseline_calories_records(self, bulk_data: CaloriesBaselineBulkCreate, user_id: str) -> tuple:
        """Create or update multiple baseline calories records (bulk upsert)"""

        created_count = 0
        updated_count = 0
        processed_records = []

        metrics_repository = MetricsRepository(self.db)

        for baseline_data in bulk_data.records:
            data_source = baseline_data.source
            existing_record = metrics_repository.get_baseline_calories_by_date_source(
                user_id=user_id,
                date_hour=baseline_data.date_hour,
                source=data_source,
            )

            if existing_record:
                if baseline_data.baseline_calories is not None:
                    existing_record.baseline_calories = baseline_data.baseline_calories
                if baseline_data.bmr is not None:
                    existing_record.bmr = baseline_data.bmr
                existing_record.updated_at = datetime.now(timezone.utc)
                updated_record = metrics_repository.update_baseline_calories_record(existing_record)
                processed_records.append(updated_record)
                updated_count += 1
            else:
                new_record = CaloriesBaseline(
                    id=generate_rid("metric", "calories_baseline"),
                    user_id=user_id,
                    date_hour=baseline_data.date_hour,
                    baseline_calories=baseline_data.baseline_calories,
                    bmr=baseline_data.bmr,
                    source=data_source,
                )
                new_record = metrics_repository.create_baseline_calories_record(new_record)
                processed_records.append(new_record)
                created_count += 1

        return processed_records, created_count, updated_count

    def get_baseline_calories_record(self, user_id: str, record_id: str) -> Optional[CaloriesBaseline]:
        """Get a specific baseline calories record by ID"""
        metrics_repository = MetricsRepository(self.db)
        return metrics_repository.get_baseline_calories_record(user_id, record_id)

    def delete_baseline_calories_record(self, user_id: str, record_id: str) -> Optional[CaloriesBaseline]:
        """Delete a baseline calories record"""
        metrics_repository = MetricsRepository(self.db)
        return metrics_repository.delete_baseline_calories_record(user_id, record_id)

# Sleep Daily Services

    def get_sleep_daily_data(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[SleepDaily]:
        """Get sleep daily data with optional date filtering"""
        metrics_repository = MetricsRepository(self.db)
        return metrics_repository.get_sleep_daily_data(user_id, start_date, end_date)

    def create_or_update_multiple_sleep_daily_records(self, bulk_data: SleepDailyBulkCreate, user_id: str) -> tuple:
        """Create or update multiple sleep daily records (bulk upsert)"""

        created_count = 0
        updated_count = 0
        processed_records = []

        metrics_repository = MetricsRepository(self.db)

        for sleep_data in bulk_data.records:
            data_source = sleep_data.source
            existing_record = metrics_repository.get_sleep_daily_by_date_source(
                user_id=user_id,
                date_day=sleep_data.date_day,
                source=data_source,
            )

            if existing_record:
                if sleep_data.bedtime is not None:
                    existing_record.bedtime = sleep_data.bedtime
                if sleep_data.wake_time is not None:
                    existing_record.wake_time = sleep_data.wake_time
                if sleep_data.total_sleep_minutes is not None:
                    existing_record.total_sleep_minutes = sleep_data.total_sleep_minutes
                if sleep_data.deep_sleep_minutes is not None:
                    existing_record.deep_sleep_minutes = sleep_data.deep_sleep_minutes
                if sleep_data.light_sleep_minutes is not None:
                    existing_record.light_sleep_minutes = sleep_data.light_sleep_minutes
                if sleep_data.rem_sleep_minutes is not None:
                    existing_record.rem_sleep_minutes = sleep_data.rem_sleep_minutes
                if sleep_data.awake_minutes is not None:
                    existing_record.awake_minutes = sleep_data.awake_minutes
                if sleep_data.sleep_efficiency is not None:
                    existing_record.sleep_efficiency = sleep_data.sleep_efficiency
                if sleep_data.sleep_quality_score is not None:
                    existing_record.sleep_quality_score = sleep_data.sleep_quality_score
                if sleep_data.notes is not None:
                    existing_record.notes = sleep_data.notes
                existing_record.updated_at = datetime.now(timezone.utc)
                updated_record = metrics_repository.update_sleep_daily_record(existing_record)
                processed_records.append(updated_record)
                updated_count += 1
            else:
                new_record = SleepDaily(
                    id=generate_rid("metric", "sleep_daily"),
                    user_id=user_id,
                    date_day=sleep_data.date_day,
                    bedtime=sleep_data.bedtime,
                    wake_time=sleep_data.wake_time,
                    total_sleep_minutes=sleep_data.total_sleep_minutes,
                    deep_sleep_minutes=sleep_data.deep_sleep_minutes,
                    light_sleep_minutes=sleep_data.light_sleep_minutes,
                    rem_sleep_minutes=sleep_data.rem_sleep_minutes,
                    awake_minutes=sleep_data.awake_minutes,
                    sleep_efficiency=sleep_data.sleep_efficiency,
                    sleep_quality_score=sleep_data.sleep_quality_score,
                    source=data_source,
                    notes=sleep_data.notes,
                )
                new_record = metrics_repository.create_sleep_daily_record(new_record)
                processed_records.append(new_record)
                created_count += 1

        return processed_records, created_count, updated_count

    def get_sleep_daily_record(self, user_id: str, record_id: str) -> Optional[SleepDaily]:
        """Get a specific sleep daily record by ID"""
        metrics_repository = MetricsRepository(self.db)
        return metrics_repository.get_sleep_daily_record(user_id, record_id)

    def delete_sleep_daily_record(self, user_id: str, record_id: str) -> Optional[SleepDaily]:
        """Delete a sleep daily record"""
        metrics_repository = MetricsRepository(self.db)
        return metrics_repository.delete_sleep_daily_record(user_id, record_id)

# Miles Services

    def get_miles_data(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[ActivityMiles]:
        """Get activity miles data with optional date filtering"""
        metrics_repository = MetricsRepository(self.db)
        return metrics_repository.get_miles_data(user_id, start_date, end_date)

    def get_miles_data_by_id(self, user_id: str, record_id: str) -> Optional[ActivityMiles]:
        """Get a specific activity miles record by ID"""
        metrics_repository = MetricsRepository(self.db)
        return metrics_repository.get_miles_data_by_id(user_id, record_id)

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
                setattr(existing_record, "updated_at", datetime.now(timezone.utc))
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
        return metrics_repository.delete_miles_record(user_id, record_id)


# Steps Services

    def get_steps_data(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[ActivitySteps]:
        """Get activity steps data with optional date filtering"""
        metrics_repository = MetricsRepository(self.db)
        return metrics_repository.get_steps_data(user_id, start_date, end_date)

    def create_or_update_multiple_steps_records(self, bulk_data: ActivityStepsBulkCreate, user_id: str) -> tuple:
        """Create or update multiple activity steps records (bulk upsert)"""

        created_count = 0
        updated_count = 0
        processed_records = []

        metrics_repository = MetricsRepository(self.db)

        for steps_data in bulk_data.records:
            existing_record = metrics_repository.get_steps_data_by_date_hour_source(user_id, steps_data.date_hour, steps_data.source)
            
            if existing_record:
                # Update existing record
                if steps_data.steps is not None:
                    setattr(existing_record, "steps", steps_data.steps)
                if steps_data.source is not None:
                    setattr(existing_record, "source", steps_data.source)
                setattr(existing_record, "updated_at", datetime.now(timezone.utc))
                updated_record = metrics_repository.update_steps_record(existing_record)
                processed_records.append(updated_record)
                updated_count += 1
            else:
                # Create new activity steps record
                new_record = ActivitySteps(
                    id=generate_rid("metric", "activity_steps"),
                    user_id=user_id,
                    date_hour=steps_data.date_hour,
                    steps=steps_data.steps,
                    source=steps_data.source,
                )
                new_record = metrics_repository.create_new_steps_record(new_record)
                processed_records.append(new_record)
                created_count += 1

        return processed_records, created_count, updated_count

    def get_steps_data_by_id(self, user_id: str, record_id: str) -> Optional[ActivitySteps]:
        """Get a specific activity steps record by ID"""
        metrics_repository = MetricsRepository(self.db)
        return metrics_repository.get_steps_data_by_id(user_id, record_id)

    def delete_steps_record(self, user_id: str, record_id: str) -> Optional[ActivitySteps]:
        """Delete an activity steps record"""
        metrics_repository = MetricsRepository(self.db)
        return metrics_repository.delete_steps_record(user_id, record_id)

# Workouts Services

    def get_workouts_data(self, user_id: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[ActivityWorkouts]:
        """Get activity workouts data with optional date filtering"""
        metrics_repository = MetricsRepository(self.db)
        return metrics_repository.get_workouts_data(user_id, start_date, end_date)

    def get_workouts_data_by_id(self, user_id: str, record_id: str) -> Optional[ActivityWorkouts]:
        """Get a specific activity workout record by ID"""
        metrics_repository = MetricsRepository(self.db)
        return metrics_repository.get_workouts_data_by_id(user_id, record_id)

    def create_or_update_multiple_workouts_records(self, bulk_data: ActivityWorkoutsBulkCreate, user_id: str) -> tuple:
        """Create or update multiple activity workouts records (bulk upsert)"""
        
        created_count = 0
        updated_count = 0
        processed_records = []

        metrics_repository = MetricsRepository(self.db)

        for workout_data in bulk_data.records:
            # Check if record already exists for this date and source
            existing_record = metrics_repository.get_workouts_data_by_date_source(user_id, workout_data.date, workout_data.source)

            if existing_record:
                # Update existing record
                if workout_data.workout_name is not None:
                    setattr(existing_record, "workout_name", workout_data.workout_name)
                if workout_data.workout_type is not None:
                    setattr(existing_record, "workout_type", workout_data.workout_type)
                if workout_data.duration_minutes is not None:
                    setattr(
                        existing_record,
                        "duration_minutes",
                        workout_data.duration_minutes,
                    )
                if workout_data.calories_burned is not None:
                    setattr(
                        existing_record, "calories_burned", workout_data.calories_burned
                    )
                if workout_data.distance_miles is not None:
                    setattr(
                        existing_record, "distance_miles", workout_data.distance_miles
                    )
                if workout_data.avg_heart_rate is not None:
                    setattr(
                        existing_record, "avg_heart_rate", workout_data.avg_heart_rate
                    )
                if workout_data.max_heart_rate is not None:
                    setattr(
                        existing_record, "max_heart_rate", workout_data.max_heart_rate
                    )
                if workout_data.intensity is not None:
                    setattr(existing_record, "intensity", workout_data.intensity)
                if workout_data.notes is not None:
                    setattr(existing_record, "notes", workout_data.notes)
                setattr(existing_record, "updated_at", datetime.now(timezone.utc))
                updated_record = metrics_repository.update_workouts_record(existing_record)
                processed_records.append(updated_record)
                updated_count += 1
            else:
                # Create new workout record
                new_record = ActivityWorkouts(
                    id=generate_rid("metric", "activity_workouts"),
                    user_id=user_id,
                    date=workout_data.date,
                    workout_name=workout_data.workout_name,
                    workout_type=workout_data.workout_type,
                    duration_minutes=workout_data.duration_minutes,
                    calories_burned=workout_data.calories_burned,
                    distance_miles=workout_data.distance_miles,
                    avg_heart_rate=workout_data.avg_heart_rate,
                    max_heart_rate=workout_data.max_heart_rate,
                    intensity=workout_data.intensity,
                    source=workout_data.source,
                    notes=workout_data.notes,
                )
                new_record = metrics_repository.create_new_workouts_record(new_record)
                processed_records.append(new_record)
                created_count += 1
        
        return processed_records, created_count, updated_count

    def delete_workouts_record(self, user_id: str, record_id: str) -> Optional[ActivityWorkouts]:
        """Delete an activity workouts record"""
        metrics_repository = MetricsRepository(self.db)
        return metrics_repository.delete_workouts_record(user_id, record_id)
