from fastapi import APIRouter

from app.api.v1.nutrition import macros

# Create the nutrition router
router = APIRouter(prefix="/api/v1/nutrition")

# Include all nutrition sub-routers
router.include_router(macros.router)
