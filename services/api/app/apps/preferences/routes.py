from fastapi import APIRouter, Depends, Path

from services.api.app.apps.auth import dependencies as auth_dependencies
from services.api.app.apps.preferences.schemas import UserPreferencesResponse, UpdateUserPreferencesRequest
from services.api.app.apps.preferences.service import PreferencesService
from services.api.app.dependencies import get_preferences_service

router = APIRouter()


@router.get("/user-preferences/{user_id}")
async def get_user_preferences(
    _=Depends(auth_dependencies.validate_user),
    service: PreferencesService = Depends(get_preferences_service),
    user_id: int = Path(..., gt=0),
) -> UserPreferencesResponse:
    return await service.get_user_preference(user_id=user_id)


@router.patch("/user-preferences/{user_id}")
async def change_user_preferences(
    data: UpdateUserPreferencesRequest,
    _=Depends(auth_dependencies.validate_user),
    service: PreferencesService = Depends(get_preferences_service),
    user_id: int = Path(..., gt=0),
) -> UserPreferencesResponse:
    return await service.update_user_preferences(
        user_id=user_id,
        preferences=data,
    )
