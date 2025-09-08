from fastapi import APIRouter

from app.api.v1.system.health import router as health_router

router = APIRouter(prefix="/api/v1/system")

router.include_router(health_router)
