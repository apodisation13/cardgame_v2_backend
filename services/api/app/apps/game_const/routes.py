from fastapi import APIRouter, Depends
from services.api.app.apps.auth import dependencies as auth_dependencies
from services.api.app.apps.game_const.service import GameConstService
from services.api.app.dependencies import get_game_const_service


router = APIRouter()


@router.get("")
async def get_game_const(
    _=Depends(auth_dependencies.is_user_authorized),
    service: GameConstService = Depends(get_game_const_service),
) -> dict:
    return await service.get_game_const()
