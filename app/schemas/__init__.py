# Import all schemas to ensure they are available
# This file makes all schemas easily accessible

# Auth schemas
from .auth.user import (
    Token,
    TokenData,
    UserCreate,
    UserDeleteResponse,
    UserLogin,
    UserResponse,
    UserUpdate,
    UserUpdateResponse,
)

# Goal schemas
from .goal.general import (
    GoalGeneralCreate,
    # GoalGeneralCreateResponse,
    GoalGeneralDeleteResponse,
    GoalGeneralResponse,
    # GoalGeneralUpdate,
    # GoalGeneralUpdateResponse,
)
from .goal.macros import (
    GoalMacrosCreate,
    GoalMacrosCreateResponse,
    GoalMacrosDeleteResponse,
    GoalMacrosResponse,
    GoalMacrosUpdate,
    GoalMacrosUpdateResponse,
)
from .metric.activity.miles import (
    ActivityMilesCreate,
    ActivityMilesCreateResponse,
    ActivityMilesDeleteResponse,
    ActivityMilesExportResponse,
    ActivityMilesResponse,
)
from .metric.activity.steps import (
    ActivityStepsCreate,
    ActivityStepsCreateResponse,
    ActivityStepsDeleteResponse,
    ActivityStepsExportResponse,
    ActivityStepsIngestRequest,
    ActivityStepsIngestResponse,
    ActivityStepsResponse,
    StepsDataPoint,
    StepsMetric,
)
from .metric.activity.workouts import (
    ActivityWorkoutsCreate,
    ActivityWorkoutsCreateResponse,
    ActivityWorkoutsDeleteResponse,
    ActivityWorkoutsExportResponse,
    ActivityWorkoutsResponse,
)

# Metric schemas
from .metric.body.composition import (
    BodyCompositionCreate,
    BodyCompositionCreateResponse,
    BodyCompositionDeleteResponse,
    BodyCompositionExportResponse,
    BodyCompositionResponse,
)
from .metric.body.heartrate import (
    HeartRateCreate,
    HeartRateCreateResponse,
    HeartRateDeleteResponse,
    HeartRateExportRecord,
    HeartRateExportResponse,
    HeartRateResponse,
)
from .metric.calories.active import (
    ActiveCaloriesDataPoint,
    ActiveCaloriesExportResponse,
    ActiveCaloriesIngestRequest,
    ActiveCaloriesIngestResponse,
    ActiveCaloriesMetric,
    ActiveCaloriesRecord,
)
from .metric.calories.baseline import (
    CaloriesBaselineCreate,
    CaloriesBaselineCreateResponse,
    CaloriesBaselineDeleteResponse,
    CaloriesBaselineExportResponse,
    CaloriesBaselineResponse,
)
from .metric.sleep.daily import (
    SleepDailyCreate,
    SleepDailyCreateResponse,
    SleepDailyDeleteResponse,
    SleepDailyExportResponse,
    SleepDailyResponse,
)

# Nutrition schemas
from .nutrition.macros import (
    DailyAggregation,
    DailyAggregationResponse,
    MacroDataPoint,
    NutritionMacrosDeleteResponse,
    NutritionMacrosExportResponse,
    NutritionMacrosIngestRequest,
    NutritionMacrosIngestResponse,
    NutritionMacrosRecord,
    NutritionMacrosRecordCreate,
    NutritionMacrosRecordResponse,
)

__all__ = [
    # Auth
    "Token",
    "TokenData",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "UserUpdate",
    "UserUpdateResponse",
    "UserDeleteResponse",
    # Goal
    "GoalGeneralCreate",
    "GoalGeneralUpdate",
    "GoalGeneralResponse",
    "GoalGeneralCreateResponse",
    "GoalGeneralUpdateResponse",
    "GoalGeneralDeleteResponse",
    "GoalMacrosCreate",
    "GoalMacrosUpdate",
    "GoalMacrosResponse",
    "GoalMacrosCreateResponse",
    "GoalMacrosUpdateResponse",
    "GoalMacrosDeleteResponse",
    # Metric - Body
    "BodyCompositionCreate",
    "BodyCompositionResponse",
    "BodyCompositionCreateResponse",
    "BodyCompositionDeleteResponse",
    "BodyCompositionExportResponse",
    "HeartRateCreate",
    "HeartRateCreateResponse",
    "HeartRateDeleteResponse",
    "HeartRateExportRecord",
    "HeartRateExportResponse",
    "HeartRateResponse",
    # Metric - Activity
    "StepsDataPoint",
    "StepsMetric",
    "ActivityStepsCreate",
    "ActivityStepsResponse",
    "ActivityStepsCreateResponse",
    "ActivityStepsDeleteResponse",
    "ActivityStepsExportResponse",
    "ActivityStepsIngestRequest",
    "ActivityStepsIngestResponse",
    "ActivityMilesCreate",
    "ActivityMilesResponse",
    "ActivityMilesCreateResponse",
    "ActivityMilesDeleteResponse",
    "ActivityMilesExportResponse",
    "ActivityWorkoutsCreate",
    "ActivityWorkoutsResponse",
    "ActivityWorkoutsCreateResponse",
    "ActivityWorkoutsDeleteResponse",
    "ActivityWorkoutsExportResponse",
    # Metric - Calories
    "CaloriesBaselineCreate",
    "CaloriesBaselineResponse",
    "CaloriesBaselineCreateResponse",
    "CaloriesBaselineDeleteResponse",
    "CaloriesBaselineExportResponse",
    "ActiveCaloriesDataPoint",
    "ActiveCaloriesMetric",
    "ActiveCaloriesRecord",
    "ActiveCaloriesIngestRequest",
    "ActiveCaloriesIngestResponse",
    "ActiveCaloriesExportResponse",
    # Metric - Sleep
    "SleepDailyCreate",
    "SleepDailyResponse",
    "SleepDailyCreateResponse",
    "SleepDailyDeleteResponse",
    "SleepDailyExportResponse",
    # Nutrition
    "MacroDataPoint",
    "NutritionMacrosIngestRequest",
    "NutritionMacrosIngestResponse",
    "NutritionMacrosRecord",
    "NutritionMacrosExportResponse",
    "NutritionMacrosRecordCreate",
    "NutritionMacrosRecordResponse",
    "DailyAggregation",
    "DailyAggregationResponse",
    "NutritionMacrosDeleteResponse",
]
