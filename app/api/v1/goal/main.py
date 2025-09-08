from fastapi import APIRouter

from app.api.v1.goal import general, macros, weight

# Create the goal router
router = APIRouter(prefix="/api/v1/goal")

# Include all goal sub-routers
router.include_router(general.router)
router.include_router(macros.router)
router.include_router(weight.router)
