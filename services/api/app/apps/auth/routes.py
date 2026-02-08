from fastapi import APIRouter, Depends
from fastapi.params import Path
from services.api.app.apps.auth import dependencies as auth_dependencies
from services.api.app.apps.auth.schemas import (
    UserLoginRequest,
    UserLoginResponse,
    UserRegisterRequest,
    UserRegisterResponse, RefreshTokenRequest, RefreshTokenResponse,
)
from services.api.app.apps.auth.service import AuthService
from services.api.app.dependencies import get_auth_service


router = APIRouter()


@router.post("/register-user")
async def register(
    user_data: UserRegisterRequest,
    service: AuthService = Depends(get_auth_service),
) -> UserRegisterResponse:
    """
    Роут регистрации пользователя:
    1) Присылаем с фронта почту, ник пользователя и голый пароль
    2) Создаем юзера или кидаем ошибку, что пользователь с такой почтой/ником уже существует
    3) Открываем юзеру то, что открыто по умолчанию: cards, leaders, base-deck, levels, resources
    4) TODO: здесь нужно сделать отправку кода подтверждения на почту
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
    4) Создаем по его почте уникальный токен - access_token + refresh_token
    """
    return await service.login_user(user_data=user_data)


@router.post("/refresh-token")
async def refresh_token(
    user_data: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
) -> RefreshTokenResponse:
    """
    Роут для обновления протухшего access_token
    Каждый раз, когда у пользователя протух access_token, присылаем сюда refresh_token и получаем новый access_token
    """
    return await service.refresh_access_token(user_data=user_data)
