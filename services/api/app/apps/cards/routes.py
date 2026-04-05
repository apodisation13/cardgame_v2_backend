from fastapi import APIRouter, Depends, Request
from services.api.app.apps.auth import dependencies as auth_dependencies
from services.api.app.apps.cards.schemas import CardsResponse
from services.api.app.apps.cards.service import CardsService
from services.api.app.dependencies import get_cards_service


router = APIRouter()


@router.get("")
async def get_cards(
    request: Request,
    _=Depends(auth_dependencies.is_user_authorized),
    user_cards_service: CardsService = Depends(get_cards_service),
) -> CardsResponse:
    return await user_cards_service.get_cards(
        base_url=str(request.base_url),
    )
