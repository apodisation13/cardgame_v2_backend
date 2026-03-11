from typing import Optional

from fastapi import APIRouter, Depends, Request, Path, Query
from services.api.app.apps.auth import dependencies as auth_dependencies
from services.api.app.apps.stats.schemas import GetStatsResponse
from services.api.app.apps.stats.service import StatsService
from services.api.app.dependencies import get_stats_service


router = APIRouter()


@router.get("/{user_id}/stats")
async def open_user_related_levels(
    _=Depends(auth_dependencies.validate_user),
    stats_service: StatsService = Depends(get_stats_service),
    user_id: int = Path(..., gt=0),
    for_user: Optional[int] = Query(None),
) -> GetStatsResponse:
    return await stats_service.get_user_stats(
        user_id=user_id,
        for_user=int(for_user) if for_user else None,
    )
