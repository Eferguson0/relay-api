from fastapi import APIRouter

from app.api.v1.nutrition import macros, foods, consumption_logs

# Create the nutrition router
router = APIRouter(prefix="/nutrition")

# Include all nutrition sub-routers
router.include_router(macros.router)
router.include_router(foods.router)
router.include_router(consumption_logs.router)
