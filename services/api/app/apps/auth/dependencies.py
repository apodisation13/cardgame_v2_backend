import logging
from typing import TYPE_CHECKING, Optional

from fastapi import Depends, HTTPException, Header, status
from services.api.app.apps.auth.service import AuthService
from services.api.app.dependencies import get_auth_service


if TYPE_CHECKING:
    from services.api.app.apps.auth.schemas import UserCheckTokenResponse


logger = logging.getLogger(__name__)


def get_token_from_header(
    authorization: Optional[str] = Header(None, alias="Authorization"),
) -> str:
    """
    Ожидаем токен в заголовках в виде
    Authorization: Bearer <TOKEN>
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization format. Use 'Bearer <token>'",
        )

    return authorization.split(" ")[1]


async def validate_user(
    user_id: int,
    token: str = Depends(get_token_from_header),
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    user: UserCheckTokenResponse = await auth_service.get_user_by_token(token=token)

    if user.id != user_id:
        logger.error("User %s trying to access another user's data %s", user.id, user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access denied",
        )


async def is_user_authorized(
    token: str = Depends(get_token_from_header),
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    user: UserCheckTokenResponse = await auth_service.get_user_by_token(token=token)

    if not user:
        logger.error("User is not authorized")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access denied",
        )
