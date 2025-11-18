from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from services.api.app.apps.auth.schemas import UserRegister
from services.api.app.apps.auth.service import AuthService
from services.api.app.dependencies import get_auth_service


security_s = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_s),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserRegister:
    return await auth_service.get_current_user(credentials.credentials)
