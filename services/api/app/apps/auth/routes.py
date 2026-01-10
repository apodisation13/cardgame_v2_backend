import logging

from fastapi import APIRouter, Depends
from fastapi.params import Path
from services.api.app.apps.auth import dependencies as auth_dependencies
from services.api.app.apps.auth.schemas import (
    UserLoginRequest,
    UserLoginResponse,
    UserRegisterRequest,
    UserRegisterResponse,
)
from services.api.app.apps.auth.service import AuthService
from services.api.app.dependencies import get_auth_service


logger = logging.getLogger(__name__)


router = APIRouter()


# @router.get("/list-users")
# async def get_users(
#     service: AuthService = Depends(get_auth_service),
#     config: Config = Depends(get_config),
# ) -> list[User]:
#     logger.info("STR17, %s, %s", type(config), config.AAA)
#     return await service.get_users()


@router.post("/register-user")
async def register(
    user_data: UserRegisterRequest,
    service: AuthService = Depends(get_auth_service),
) -> UserRegisterResponse:
    """
    Роут регистрации пользователя:
    1) Присылаем с фронта почту, ник пользователя и голый пароль
    2) Создаем юзера или кидаем ошибку, что пользователь с такой почтой/ником уже существует
    3) TODO: здесь нужно сделать отправку кода подтверждения на почту
    """
    return await service.register_user(user_data=user_data)


@router.post("/login-user")
async def login_user(
    user_data: UserLoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> UserLoginResponse:
    """
    Роут аутентификации пользователя:
    1) С фронта приходит почта пользователя и голый пароль
    2) Проверяем по почте, есть ли такой пользователь, если нет - кидаем ошибку
    3) Проверяем его пароль (голый пароль и зашифрованный в базе)
    4) Создаем по его почте уникальный токен
    """
    return await service.login(user_data=user_data)


@router.get("/users/{user_id}")
async def read_users_me(
    current_user: UserRegisterRequest = Depends(auth_dependencies.get_current_user),
    user_id: int = Path(..., gt=0),
) -> UserRegisterRequest:
    print("STR63", user_id)
    return current_user
