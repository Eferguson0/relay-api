import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.auth.user import AuthUser
from app.schemas.nutrition.foods import (
    FoodCreate,
    FoodCreateResponse,
    FoodDeleteResponse,
    FoodListResponse,
    FoodResponse,
    FoodUpdate,
)
from app.services.auth_service import get_current_active_user
from app.services.nutrition_service import NutritionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/foods", tags=["nutrition-foods"])


@router.get(
    "/",
    response_model=FoodListResponse,
    summary="List foods",
    description="Retrieve foods available to the user",
    responses={
        200: {"description": "Foods retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        500: {"description": "Internal server error"},
    },
)
async def list_foods(
    search: Optional[str] = Query(
        default=None, description="Partial name search for foods"
    ),
    limit: int = Query(
        default=50, ge=1, le=100, description="Maximum number of foods to return (default: 50, max: 100)"
    ),
    offset: int = Query(
        default=0, ge=0, description="Number of foods to skip (default: 0)"
    ),
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
) -> FoodListResponse:
    """Return foods filtered by optional search criteria."""
    try:
        nutrition_service = NutritionService(db)
        foods, total_count = nutrition_service.list_foods(
            search=search,
            limit=limit,
            offset=offset,
        )
        return FoodListResponse(
            records=[FoodResponse.model_validate(food) for food in foods],
            total_count=total_count,
        )
    except Exception as exc:
        logger.error(f"Error listing foods for user {current_user.id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving foods",
        ) from exc


@router.post(
    "/",
    response_model=FoodCreateResponse,
    summary="Create food",
    description="Create a new food definition",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Food created successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        500: {"description": "Internal server error"},
    },
)
async def create_food(
    food_data: FoodCreate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
) -> FoodCreateResponse:
    """Create a new food entry."""
    try:
        nutrition_service = NutritionService(db)
        food = nutrition_service.create_food(food_data)
        return FoodCreateResponse(
            message="Food created successfully",
            food=FoodResponse.model_validate(food),
        )
    except Exception as exc:
        logger.error(f"Error creating food for user {current_user.id}: {exc}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating food",
        ) from exc


@router.get(
    "/{food_id}",
    response_model=FoodResponse,
    summary="Get food",
    description="Retrieve a single food by ID",
    responses={
        200: {"description": "Food retrieved successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Food not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_food(
    food_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
) -> FoodResponse:
    """Get a single food definition."""
    try:
        nutrition_service = NutritionService(db)
        food = nutrition_service.get_food(food_id)
        if not food:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Food not found"
            )
        return FoodResponse.model_validate(food)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error retrieving food {food_id} for user {current_user.id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving food",
        ) from exc


@router.put(
    "/{food_id}",
    response_model=FoodResponse,
    summary="Update food",
    description="Update an existing food definition",
    responses={
        200: {"description": "Food updated successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Food not found"},
        500: {"description": "Internal server error"},
    },
)
async def update_food(
    food_id: str,
    food_data: FoodUpdate,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
) -> FoodResponse:
    """Update an existing food."""
    try:
        nutrition_service = NutritionService(db)
        food = nutrition_service.get_food(food_id)
        if not food:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Food not found"
            )

        updated_food = nutrition_service.update_food(food, food_data)
        return FoodResponse.model_validate(updated_food)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error updating food {food_id} for user {current_user.id}: {exc}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating food",
        ) from exc


@router.delete(
    "/{food_id}",
    response_model=FoodDeleteResponse,
    summary="Delete food",
    description="Delete a food definition",
    responses={
        200: {"description": "Food deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Inactive user"},
        404: {"description": "Food not found"},
        500: {"description": "Internal server error"},
    },
)
async def delete_food(
    food_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_active_user),
) -> FoodDeleteResponse:
    """Delete a food entry."""
    try:
        nutrition_service = NutritionService(db)
        food = nutrition_service.get_food(food_id)
        if not food:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Food not found"
            )

        nutrition_service.delete_food(food)
        return FoodDeleteResponse(
            message=f"Food {food_id} deleted successfully",
            deleted_count=1,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Error deleting food {food_id} for user {current_user.id}: {exc}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting food",
        ) from exc
