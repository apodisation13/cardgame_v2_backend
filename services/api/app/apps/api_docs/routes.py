from fastapi import APIRouter, Depends, Request
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from services.api.app.apps.auth.service import AuthService
from services.api.app.dependencies import get_auth_service
from starlette.responses import HTMLResponse


router = APIRouter()

security_basic = HTTPBasic()


async def check_developer_credentials(
    credentials: HTTPBasicCredentials = Depends(security_basic),
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    await auth_service.get_developer_user(email=credentials.username)


@router.get(
    path="/docs",
    include_in_schema=False,
    dependencies=[Depends(check_developer_credentials)],
)
async def get_documentation() -> HTMLResponse:
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Docs",
        swagger_ui_parameters={"persistAuthorization": False},
    )


@router.get(
    path="/openapi.json",
    include_in_schema=False,
    dependencies=[Depends(check_developer_credentials)],
)
async def openapi(
    request: Request,
) -> dict:
    return get_openapi(
        title=request.app.title,
        version=request.app.version,
        routes=request.app.routes,
    )
