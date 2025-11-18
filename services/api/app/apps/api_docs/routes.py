from fastapi import APIRouter, Depends, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from services.api.app.apps.auth.service import AuthService
from services.api.app.dependencies import get_auth_service


router = APIRouter()

security_basic = HTTPBasic()


async def check_developer_credentials(
    credentials: HTTPBasicCredentials = Depends(security_basic),
    service: AuthService = Depends(get_auth_service),
):
    user = await service._get_user_from_db(email=credentials.username)
    return user


@router.get("/docs", include_in_schema=False)
async def get_documentation(
    current_developer: AuthService = Depends(check_developer_credentials),
):
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Docs",
        swagger_ui_parameters={"persistAuthorization": False},
    )


@router.get("/openapi.json", include_in_schema=False)
async def openapi(
    request: Request,
    current_developer: AuthService = Depends(check_developer_credentials),
):
    return get_openapi(
        title=request.app.title,
        version=request.app.version,
        routes=request.app.routes,
    )
