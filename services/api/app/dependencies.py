from fastapi import Depends, FastAPI
from lib.utils.db.pool import Database
from services.api.app.apps.auth.service import AuthService
from services.api.app.apps.news.service import NewsService
from services.api.app.apps.progress.service import UserProgressService
from services.api.app.config import Config


# Глобальная переменная для доступа к app
_app: FastAPI = None


def set_global_app(
    app: FastAPI,
) -> None:
    global _app
    _app = app


async def get_config() -> Config:
    return _app.state.config


async def get_db() -> Database:
    return _app.state.db


async def get_auth_service(
    db_pool: Database = Depends(get_db),
    config: Config = Depends(get_config),
) -> AuthService:
    return AuthService(
        db_pool=db_pool,
        config=config,
    )


async def get_news_service(
    db_pool: Database = Depends(get_db),
    config: Config = Depends(get_config),
) -> NewsService:
    return NewsService(
        db_pool=db_pool,
        config=config,
    )


async def get_user_progress_service(
    db_pool: Database = Depends(get_db),
    config: Config = Depends(get_config),
) -> UserProgressService:
    return UserProgressService(
        db_pool=db_pool,
        config=config,
    )
