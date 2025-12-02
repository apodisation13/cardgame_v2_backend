import pytest

from fastapi import FastAPI
from httpx import AsyncClient
from lib.utils.db.pool import Database
import pytest_asyncio
from services.api.app.config import Config, get_config
from services.api.app.config import get_config as get_app_settings
from services.api.app.main import app as fastapi_app


@pytest_asyncio.fixture
async def app(db_pool) -> FastAPI:
    """Настроенное приложение FastAPI для тестов"""
    # Устанавливаем тестовый конфиг
    fastapi_app.state.config = get_app_settings()

    # Создаем Database обертку используя существующий пул из фикстуры
    db = Database(fastapi_app.state.config)
    # Переопределяем метод connect чтобы использовать существующий пул
    db.pool = db_pool
    fastapi_app.state.db = db

    # Устанавливаем глобальное приложение
    from services.api.app.dependencies import set_global_app

    set_global_app(fastapi_app)

    yield fastapi_app


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncClient:
    """Асинхронный клиент для тестирования API"""
    async with AsyncClient(app=app, base_url="http://test", headers={"Content-Type": "application/json"}) as ac:
        yield ac


@pytest.fixture(scope="session")
def config() -> Config:
    return get_config()
