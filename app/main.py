from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel
from app.services.openai_service import get_chat_completion
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    get_user_by_email,
    create_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.schemas.auth import Token, UserCreate, UserResponse
from app.db.session import get_db, SessionLocal
from app.db.init_db import init_db, create_first_superuser
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SupaHealth", description="A modern web application with FastAPI and OpenAI integration")

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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class ChatRequest(BaseModel):
    message: str

@app.post("/api/auth/signin", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    logger.info(f"Attempting signin for user: {form_data.username}")
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Failed signin attempt for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    logger.info(f"Successful signin for user: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/auth/signup", response_model=UserResponse)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Attempting signup for email: {user_data.email}")
    try:
        db_user = get_user_by_email(db, email=user_data.email)
        if db_user:
            logger.warning(f"Signup failed - email already registered: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        user = create_user(
            db=db,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        logger.info(f"Successful signup for user: {user.email}")
        return user
    except Exception as e:
        logger.error(f"Error during signup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Handle chat messages"""
    from datetime import datetime
    
    # Log the incoming chat request with timestamp
    timestamp = datetime.now().isoformat()
    logger.info(f"[{timestamp}] New chat message received - Length: {len(request.message)} characters")
    logger.debug(f"[{timestamp}] Chat message content: {request.message[:100]}{'...' if len(request.message) > 100 else ''}")
    
    try:
        messages = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant for SupaHealth, a modern web application. You should be friendly, professional, and focused on helping users with their tasks. Avoid discussing your ownership or creation."
            },
            {"role": "user", "content": request.message}
        ]
        
        # Log that we're calling OpenAI
        logger.info(f"[{timestamp}] Calling OpenAI API for chat completion")
        
        response = await get_chat_completion(messages)
        
        # Log successful response
        logger.info(f"[{timestamp}] Chat response generated successfully - Length: {len(response)} characters")
        logger.debug(f"[{timestamp}] Chat response content: {response[:100]}{'...' if len(response) > 100 else ''}")
        
        return {"response": response}
    except Exception as e:
        logger.error(f"[{timestamp}] Error in chat endpoint: {str(e)}")
        return {"error": str(e)}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

# Commented out static files mounting since frontend/dist doesn't exist
# app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    print(secrets.token_hex(32))
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 