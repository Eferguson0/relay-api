import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.auth.user import AuthUser
from app.schemas.nutrition.user_food_preferences import (
    UserFoodPreferenceCreate,
    UserFoodPreferenceCreateResponse,
    UserFoodPreferenceDeleteResponse,
    UserFoodPreferenceListResponse,
    UserFoodPreferenceResponse,
    UserFoodPreferenceUpdate,
)
from app.services.auth_service import get_current_active_user
from app.services.nutrition_service import NutritionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user-food-preferences", tags=["nutrition-preferences"])


@router.get(
    "/",
    response_model=UserFoodPreferenceListResponse,
    summary="List user food preferences",
    description="Retrieve user food preferences with optional filters",
    responses={
        200: {"description": "Preferences retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        500: {"description": "Internal server error"},
    },
)
async def list_user_food_preferences(
    is_saved: Optional[bool] = Query(
        default=None, description="Filter by saved status"
    ),
    limit: int = Query(
        default=50, ge=1, le=100, description="Maximum number of preferences to return (default: 50, max: 100)"
    ),
    offset: int = Query(
        default=0, ge=0, description="Number of preferences to skip (default: 0)"
    ),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
) -> UserFoodPreferenceListResponse:
    """Return the user's food preferences."""
    try:
        nutrition_service = NutritionService(db)
        preferences, total_count = nutrition_service.list_user_food_preferences(
            user_id=current_user.id,
            is_saved=is_saved,
            limit=limit,
            offset=offset,
        )
        return UserFoodPreferenceListResponse(
            records=[
                UserFoodPreferenceResponse.model_validate(pref)
                for pref in preferences
            ],
            total_count=total_count,
        )
    except Exception as exc:
        logger.error(
            f"Error listing food preferences for user {current_user.id}: {exc}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving food preferences",
        ) from exc


@router.post(
    "/",
    response_model=UserFoodPreferenceCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user food preference",
    description="Create a user-specific food preference",
    responses={
        201: {"description": "Preference created successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        409: {"description": "Preference already exists for this food"},
        500: {"description": "Internal server error"},
    },
)
async def create_user_food_preference(
    preference_data: UserFoodPreferenceCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
) -> UserFoodPreferenceCreateResponse:
    """Create a new user food preference."""
    try:
        nutrition_service = NutritionService(db)
        preference = nutrition_service.get_user_food_preference(
            user_id=current_user.id,
            food_id=preference_data.food_id,
        )
        if preference:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Preference already exists for this food",
            )

        new_preference = nutrition_service.create_user_food_preference(
            user_id=current_user.id,
            food_id=preference_data.food_id,
            preference_data=preference_data,
        )
        return UserFoodPreferenceCreateResponse(
            message="Food preference created successfully",
            preference=UserFoodPreferenceResponse.model_validate(new_preference),
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            f"Error creating food preference for user {current_user.id}: {exc}"
        )
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating food preference",
        ) from exc


@router.get(
    "/{food_id}",
    response_model=UserFoodPreferenceResponse,
    summary="Get user food preference",
    description="Retrieve the preference for a specific food",
    responses={
        200: {"description": "Preference retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Preference not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_user_food_preference(
    food_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
) -> UserFoodPreferenceResponse:
    """Fetch the user's preference for a food."""
    try:
        nutrition_service = NutritionService(db)
        preference = nutrition_service.get_user_food_preference(
            user_id=current_user.id,
            food_id=food_id,
        )
        if not preference:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food preference not found",
            )
        return UserFoodPreferenceResponse.model_validate(preference)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            f"Error retrieving food preference for user {current_user.id}, food {food_id}: {exc}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving food preference",
        ) from exc


@router.put(
    "/{food_id}",
    response_model=UserFoodPreferenceResponse,
    summary="Update user food preference",
    description="Update the preference for a food",
    responses={
        200: {"description": "Preference updated successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Preference not found"},
        500: {"description": "Internal server error"},
    },
)
async def update_user_food_preference(
    food_id: str,
    preference_data: UserFoodPreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
) -> UserFoodPreferenceResponse:
    """Update an existing user food preference."""
    try:
        nutrition_service = NutritionService(db)
        preference = nutrition_service.get_user_food_preference(
            user_id=current_user.id,
            food_id=food_id,
        )
        if not preference:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food preference not found",
            )

        updated_preference = nutrition_service.update_user_food_preference(
            preference=preference,
            preference_data=preference_data,
        )
        return UserFoodPreferenceResponse.model_validate(updated_preference)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            f"Error updating food preference for user {current_user.id}, food {food_id}: {exc}"
        )
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating food preference",
        ) from exc


@router.delete(
    "/{food_id}",
    response_model=UserFoodPreferenceDeleteResponse,
    summary="Delete user food preference",
    description="Delete the preference for a specific food",
    responses={
        200: {"description": "Preference deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Preference not found"},
        500: {"description": "Internal server error"},
    },
)
async def delete_user_food_preference(
    food_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
) -> UserFoodPreferenceDeleteResponse:
    """Delete the user's preference for a food."""
    try:
        nutrition_service = NutritionService(db)
        preference = nutrition_service.get_user_food_preference(
            user_id=current_user.id,
            food_id=food_id,
        )
        if not preference:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Food preference not found",
            )

        nutrition_service.delete_user_food_preference(preference)
        return UserFoodPreferenceDeleteResponse(
            message=f"Food preference for food {food_id} deleted successfully",
            deleted_count=1,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(
            f"Error deleting food preference for user {current_user.id}, food {food_id}: {exc}"
        )
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting food preference",
        ) from exc
