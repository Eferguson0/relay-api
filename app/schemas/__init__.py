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
    GoalGeneralCreateResponse,
    GoalGeneralDeleteResponse,
    GoalGeneralResponse,
    GoalGeneralUpdate,
    GoalGeneralUpdateResponse,
)
from .goal.macros import (
    GoalMacrosCreate,
    GoalMacrosCreateResponse,
    GoalMacrosDeleteResponse,
    GoalMacrosResponse,
    GoalMacrosUpdate,
    GoalMacrosUpdateResponse,
)
from .goal.weight import (
    GoalWeightCreate,
    GoalWeightCreateResponse,
    GoalWeightDeleteResponse,
    GoalWeightResponse,
    GoalWeightUpdate,
    GoalWeightUpdateResponse,
)
from .metric.activity.miles import (
    ActivityMilesCreate,
    ActivityMilesCreateResponse,
    ActivityMilesDeleteResponse,
    ActivityMilesExportResponse,
    ActivityMilesResponse,
    ActivityMilesUpdate,
    ActivityMilesUpdateResponse,
)
from .metric.activity.steps import (
    HourlyStepsExportResponse,
    HourlyStepsIngestRequest,
    HourlyStepsIngestResponse,
    StepsDataPoint,
    StepsMetric,
    StepsRecord,
)
from .metric.activity.workouts import (
    ActivityWorkoutsCreate,
    ActivityWorkoutsCreateResponse,
    ActivityWorkoutsDeleteResponse,
    ActivityWorkoutsExportResponse,
    ActivityWorkoutsResponse,
    ActivityWorkoutsUpdate,
    ActivityWorkoutsUpdateResponse,
)

# Metric schemas
from .metric.body.composition import (
    BodyCompositionCreate,
    BodyCompositionCreateResponse,
    BodyCompositionDeleteResponse,
    BodyCompositionExportResponse,
    BodyCompositionResponse,
    BodyCompositionUpdate,
    BodyCompositionUpdateResponse,
)
from .metric.body.heartrate import (
    HeartRateDataPoint,
    HeartRateExportResponse,
    HeartRateIngestRequest,
    HeartRateIngestResponse,
    HeartRateMetric,
    HeartRateRecord,
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
    CaloriesBaselineUpdate,
    CaloriesBaselineUpdateResponse,
)
from .metric.sleep.daily import (
    SleepDailyCreate,
    SleepDailyCreateResponse,
    SleepDailyDeleteResponse,
    SleepDailyExportResponse,
    SleepDailyResponse,
    SleepDailyUpdate,
    SleepDailyUpdateResponse,
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
    "GoalWeightCreate",
    "GoalWeightUpdate",
    "GoalWeightResponse",
    "GoalWeightCreateResponse",
    "GoalWeightUpdateResponse",
    "GoalWeightDeleteResponse",
    # Metric - Body
    "BodyCompositionCreate",
    "BodyCompositionUpdate",
    "BodyCompositionResponse",
    "BodyCompositionCreateResponse",
    "BodyCompositionUpdateResponse",
    "BodyCompositionDeleteResponse",
    "BodyCompositionExportResponse",
    "HeartRateDataPoint",
    "HeartRateMetric",
    "HeartRateRecord",
    "HeartRateIngestRequest",
    "HeartRateIngestResponse",
    "HeartRateExportResponse",
    # Metric - Activity
    "StepsDataPoint",
    "StepsMetric",
    "StepsRecord",
    "HourlyStepsIngestRequest",
    "HourlyStepsIngestResponse",
    "HourlyStepsExportResponse",
    "ActivityMilesCreate",
    "ActivityMilesUpdate",
    "ActivityMilesResponse",
    "ActivityMilesCreateResponse",
    "ActivityMilesUpdateResponse",
    "ActivityMilesDeleteResponse",
    "ActivityMilesExportResponse",
    "ActivityWorkoutsCreate",
    "ActivityWorkoutsUpdate",
    "ActivityWorkoutsResponse",
    "ActivityWorkoutsCreateResponse",
    "ActivityWorkoutsUpdateResponse",
    "ActivityWorkoutsDeleteResponse",
    "ActivityWorkoutsExportResponse",
    # Metric - Calories
    "CaloriesBaselineCreate",
    "CaloriesBaselineUpdate",
    "CaloriesBaselineResponse",
    "CaloriesBaselineCreateResponse",
    "CaloriesBaselineUpdateResponse",
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
    "SleepDailyUpdate",
    "SleepDailyResponse",
    "SleepDailyCreateResponse",
    "SleepDailyUpdateResponse",
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
