from fastapi import APIRouter, Depends, Path, Request
from services.api.app.apps.progress.schemas import UserProgressResponse
from services.api.app.apps.progress.service import UserProgressService
from services.api.app.dependencies import get_user_progress_service


router = APIRouter()


@router.get("/{user_id}")
async def get_user_progress(
    request: Request,
    # current_user: UserRegisterRequest = Depends(auth_dependencies.get_current_user),
    user_progress_service: UserProgressService = Depends(get_user_progress_service),
    user_id: int = Path(..., gt=0),
) -> UserProgressResponse:
    print("STR16", user_id, request.base_url)
    return await user_progress_service.get_user_progress(
        user_id=user_id,
        base_url=str(request.base_url),
    )
