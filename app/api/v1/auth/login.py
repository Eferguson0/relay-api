import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.auth.user import AuthUser
from app.schemas.auth.user import Token, UserCreate, UserResponse
from app.services.auth_service import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    AuthService,
    get_current_active_user,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/login", tags=["auth-login"])


@router.post("/",
    response_model=Token,
    summary="User login endpoint",
    description="Login a user and return an access token",
    responses={
        200: {"description": "Login successful"},
        400: {"description": "Invalid input"},
        401: {"description": "Incorrect email or password"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    logger.info(f"Attempting login for user: {form_data.username}")
    auth_service = AuthService(db)
    try:
        user = auth_service.authenticate_user(form_data.username, form_data.password)
        if not user:
            logger.warning(f"Failed login attempt for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_service.create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        logger.info(f"Successful login for user: {user.email}")
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Value error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except ValidationError as e:
        logger.error(f"Validation error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during login",
        )


@router.post("/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User signup endpoint",
    description="Create a new user account",
    responses={
        201: {"description": "User account created successfully"},
        400: {"description": "Email already registered or invalid input"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Attempting signup for email: {user_data.email}")
    auth_service = AuthService(db)
    try:
        db_user = auth_service.get_user_by_email(email=user_data.email)
        if db_user:
            logger.warning(
                f"Signup failed - email already registered: {user_data.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        user = auth_service.create_user(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        logger.info(f"Successful signup for user: {user.email}")
        return user
    except ValueError as e:
        logger.error(f"Value error during signup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except ValidationError as e:
        logger.error(f"Validation error during signup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error during signup: {str(e)}") 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user",
        )


@router.post("/refresh",
    response_model=Token,
    summary="Refresh access token endpoint",
    description="Refresh the access token for the current user",
    responses={
        200: {"description": "Token refreshed successfully"},
        400: {"description": "Invalid input"},
        401: {"description": "Unauthorized"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
async def refresh_access_token(
    current_user: AuthUser = Depends(get_current_active_user), db: Session = Depends(get_db)):
    logger.info(f"Token refresh requested for user: {current_user.email}")
    auth_service = AuthService(db)
    try:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_service.create_access_token(
            data={"sub": current_user.email}, expires_delta=access_token_expires
        )
        logger.info(f"Token refreshed successfully for user: {current_user.email}")
        return {"access_token": access_token, "token_type": "bearer"}
    except ValueError as e:
        logger.error(f"Value error during token refresh: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except ValidationError as e:
        logger.error(f"Validation error during token refresh: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error during token refresh: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error refreshing token",
        )