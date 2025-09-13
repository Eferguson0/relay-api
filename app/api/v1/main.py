from fastapi import APIRouter

from app.api.v1.auth.main import router as auth_router
from app.api.v1.chat.main import router as chat_router
from app.api.v1.goal.main import router as goal_router
from app.api.v1.metric.main import router as metric_router
from app.api.v1.nutrition.main import router as nutrition_router
from app.api.v1.system.main import router as system_router

# Create the main v1 router
router = APIRouter(prefix="/api/v1")

# Include all v1 sub-routers
router.include_router(auth_router)
router.include_router(chat_router)
router.include_router(goal_router)
router.include_router(metric_router)
router.include_router(nutrition_router)
router.include_router(system_router)
