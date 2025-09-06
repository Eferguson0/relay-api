import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from app.api import auth, chat, diet, goals, heart_rate, system, weight, workout
from app.db.init_db import create_first_superuser, init_db
from app.db.session import SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SupaHealth",
    description="A modern web application with FastAPI and OpenAI integration",
)

# Include API routers
app.include_router(system.router)
app.include_router(auth.router)
app.include_router(heart_rate.router)
app.include_router(diet.router)
app.include_router(goals.router)
app.include_router(weight.router)
app.include_router(workout.router)
app.include_router(chat.router)


# Initialize database and create first superuser
@app.on_event("startup")
async def startup_event():
    init_db()
    db = SessionLocal()
    try:
        create_first_superuser(db)
    finally:
        db.close()


# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/signin")

# Commented out static files mounting since frontend/dist doesn't exist
# app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
