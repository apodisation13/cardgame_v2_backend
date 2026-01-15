from fastapi import APIRouter, Depends, Path, Request

from services.api.app.apps.auth import dependencies as auth_dependencies

from services.api.app.apps.progress.schemas import UserProgressResponse, CreateDeckRequest, ListDecksResponse, \
    ResourcesRequest, UserResources, CardCraftMillRequest, CardCraftMillResponse, Season, OpenRelatedLevelsResponse, \
    CardCraftBonusRequest, CardCraftBonusResponse
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


@router.patch("/{user_id}/resource")
async def manage_resources(
    resource_request: ResourcesRequest,
    _ = Depends(auth_dependencies.validate_user),
    user_progress_service: UserProgressService = Depends(get_user_progress_service),
    user_id: int = Path(..., gt=0),
) -> UserResources:
    return await user_progress_service.manage_resources(
        user_id=user_id,
        resource_request=resource_request,
    )


@router.post("/{user_id}/card/{card_id}")
async def manage_craft_mill_card(
    request: Request,
    card_request: CardCraftMillRequest,
    _ = Depends(auth_dependencies.validate_user),
    user_progress_service: UserProgressService = Depends(get_user_progress_service),
    user_id: int = Path(..., gt=0),
    card_id: int = Path(..., gt=0),
) -> CardCraftMillResponse:
    return await user_progress_service.manage_craft_mill_process(
        user_id=user_id,
        card_id=card_id,
        subtype=card_request.subtype,
        base_url=str(request.base_url),
    )


@router.post("/{user_id}/craft-bonus-cards")
async def craft_bonus_cards(
    request: Request,
    craft_bonus_request: CardCraftBonusRequest,
    _ = Depends(auth_dependencies.validate_user),
    user_progress_service: UserProgressService = Depends(get_user_progress_service),
    user_id: int = Path(..., gt=0),
) -> CardCraftBonusResponse:
    return await user_progress_service.craft_bonus_cards(
        user_id=user_id,
        cards_ids=craft_bonus_request.cards_ids,
        base_url=str(request.base_url),
    )


@router.patch("/{user_id}/open-related-levels/{user_level_id}")
async def open_user_related_levels(
    request: Request,
    _ = Depends(auth_dependencies.validate_user),
    user_progress_service: UserProgressService = Depends(get_user_progress_service),
    user_id: int = Path(..., gt=0),
    user_level_id: int = Path(..., gt=0),
) -> OpenRelatedLevelsResponse:
    return await user_progress_service.open_level_related_levels(
        user_id=user_id,
        user_level_id=user_level_id,
        base_url=str(request.base_url),
    )
