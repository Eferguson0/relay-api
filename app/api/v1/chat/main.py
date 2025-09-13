from fastapi import APIRouter

from app.api.v1.chat.assistant import router as assistant_router

router = APIRouter(prefix="/chat")

router.include_router(assistant_router)
