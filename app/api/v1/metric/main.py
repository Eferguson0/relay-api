from fastapi import APIRouter

from app.api.v1.metric.activity import miles, steps, workouts
from app.api.v1.metric.body import composition, heartrate
from app.api.v1.metric.calories import active, baseline
from app.api.v1.metric.sleep import daily

# Create the metric router
router = APIRouter(prefix="/metric")

# Include all metric sub-routers
router.include_router(composition.router)
router.include_router(heartrate.router)
router.include_router(steps.router)
router.include_router(miles.router)
router.include_router(workouts.router)
router.include_router(baseline.router)
router.include_router(active.router)
router.include_router(daily.router)
