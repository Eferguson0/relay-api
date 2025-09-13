from fastapi import APIRouter

from app.api.v1.auth import login, user

# Create the auth router
router = APIRouter(prefix="/auth")

# Include all auth sub-routers
router.include_router(login.router)
router.include_router(user.router)
