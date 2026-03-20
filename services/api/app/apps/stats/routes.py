from typing import Optional

from fastapi import APIRouter, Depends, Path, Query
from services.api.app.apps.auth import dependencies as auth_dependencies
from services.api.app.apps.stats.schemas import (
    GetLeaderboardResponse,
    GetStatsResponse,
    PostLeaderboardRequest,
    PostStatsRequest,
)
from services.api.app.apps.stats.service import StatsService
from services.api.app.dependencies import get_stats_service


router = APIRouter()


@router.get("/{user_id}/stats")
async def get_user_stats(
    _=Depends(auth_dependencies.validate_user),
    stats_service: StatsService = Depends(get_stats_service),
    user_id: int = Path(..., gt=0),
    for_user: Optional[int] = Query(None),
) -> GetStatsResponse:
    return await stats_service.get_user_stats(
        user_id=user_id,
        for_user=int(for_user) if for_user else None,
    )


@router.post("/{user_id}/stats")
async def post_user_stats(
    post_stats_request: PostStatsRequest,
    _=Depends(auth_dependencies.validate_user),
    stats_service: StatsService = Depends(get_stats_service),
    user_id: int = Path(..., gt=0),
) -> dict:
    return await stats_service.post_user_stats(
        user_id=user_id,
        user_deck_id=post_stats_request.user_deck_id,
        game_type=post_stats_request.type,
    )


@router.get("/{user_id}/leaderboard")
async def get_user_leaderboard(
    _=Depends(auth_dependencies.validate_user),
    stats_service: StatsService = Depends(get_stats_service),
    user_id: int = Path(..., gt=0),
) -> list[GetLeaderboardResponse]:
    return await stats_service.get_user_leaderboard(
        user_id=user_id,
    )


@router.post("/{user_id}/leaderboard")
async def post_user_leaderboard(
    post_leaderboard_request: PostLeaderboardRequest,
    _=Depends(auth_dependencies.validate_user),
    stats_service: StatsService = Depends(get_stats_service),
    user_id: int = Path(..., gt=0),
) -> dict:
    return await stats_service.post_user_leaderboard(
        user_id=user_id,
        post_leaderboard_request=post_leaderboard_request,
    )


@router.get("/{user_id}/leaderboard-world")
async def get_world_leaderboard(
    _=Depends(auth_dependencies.validate_user),
    stats_service: StatsService = Depends(get_stats_service),
    user_id: int = Path(..., gt=0),
) -> list[GetLeaderboardResponse]:
    return await stats_service.get_world_leaderboard(
        user_id=user_id,
    )
