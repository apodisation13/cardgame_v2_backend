import logging

from fastapi import APIRouter, Depends
from services.api.app.apps.auth import dependencies as auth_dependencies
from services.api.app.apps.auth.schemas import Token, User, UserLogin, UserRegister
from services.api.app.apps.auth.service import AuthService
from services.api.app.config import Config
from services.api.app.dependencies import get_auth_service, get_config


logger = logging.getLogger(__name__)


router = APIRouter()


@router.get("/list-users")
async def get_users(
    service: AuthService = Depends(get_auth_service),
    config: Config = Depends(get_config),
) -> list[User]:
    logger.info("STR17, %s, %s", type(config), config.AAA)
    return await service.get_users()


@router.post("/register-user")
async def register(
    user_data: UserRegister,
    service: AuthService = Depends(get_auth_service),
) -> User:
    return await service.register_user(user_data=user_data)


@router.post("/login-user")
async def login_user(
    user_data: UserLogin,
    service: AuthService = Depends(get_auth_service),
) -> Token:
    return await service.login(user_data=user_data)


@router.get("/users/me", response_model=UserRegister)
async def read_users_me(
    current_user: UserRegister = Depends(auth_dependencies.get_current_user),
):
    return current_user
