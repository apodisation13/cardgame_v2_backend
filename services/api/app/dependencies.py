from fastapi import Depends, FastAPI
from services.api.app.apps.auth.service import AuthService


# Глобальная переменная для доступа к app
_app: FastAPI = None


def set_global_app(
    app: FastAPI,
):
    global _app
    _app = app


async def get_config():
    return _app.state.config


async def get_db():
    return _app.state.db


async def get_auth_service(
    db_pool = Depends(get_db),
    config = Depends(get_config),
):
    return AuthService(
        db_pool=db_pool,
        config=config,
    )
