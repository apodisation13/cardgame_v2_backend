from fastapi import APIRouter, Depends, Path, Request

from services.api.app.apps.auth import dependencies as auth_dependencies

from services.api.app.apps.progress.schemas import UserProgressResponse, CreateDeckRequest, ListDecksResponse
from services.api.app.apps.progress.service import UserProgressService
from services.api.app.dependencies import get_user_progress_service


router = APIRouter()


@router.get("/{user_id}")
async def get_user_progress(
    request: Request,
    _ = Depends(auth_dependencies.validate_user),
    user_progress_service: UserProgressService = Depends(get_user_progress_service),
    user_id: int = Path(..., gt=0),
) -> UserProgressResponse:
    return await user_progress_service.get_user_progress(
        user_id=user_id,
        base_url=str(request.base_url),
    )


@router.post("/{user_id}/create-deck")
async def create_user_deck(
    request: Request,
    deck: CreateDeckRequest,
    _ = Depends(auth_dependencies.validate_user),
    user_progress_service: UserProgressService = Depends(get_user_progress_service),
    user_id: int = Path(..., gt=0),
) -> ListDecksResponse:
    return await user_progress_service.create_user_deck(
        user_id=user_id,
        deck=deck,
        base_url=str(request.base_url),
    )


@router.delete("/{user_id}/alter-deck/{deck_id}")
async def delete_user_deck(
    request: Request,
    _ = Depends(auth_dependencies.validate_user),
    user_progress_service: UserProgressService = Depends(get_user_progress_service),
    user_id: int = Path(..., gt=0),
    deck_id: int = Path(..., gt=0),
) -> ListDecksResponse:
    return await user_progress_service.delete_user_deck(
        user_id=user_id,
        deck_id=deck_id,
        base_url=str(request.base_url),
    )


@router.patch("/{user_id}/alter-deck/{deck_id}")
async def change_user_deck(
    request: Request,
    deck: CreateDeckRequest,
    _ = Depends(auth_dependencies.validate_user),
    user_progress_service: UserProgressService = Depends(get_user_progress_service),
    user_id: int = Path(..., gt=0),
    deck_id: int = Path(..., gt=0),
) -> ListDecksResponse:
    return await user_progress_service.patch_user_deck(
        user_id=user_id,
        deck_id=deck_id,
        deck=deck,
        base_url=str(request.base_url),
    )
