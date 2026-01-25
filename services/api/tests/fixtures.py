import pytest

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from lib.utils.db.pool import Database
import pytest_asyncio
from services.api.app.apps.auth.lib import get_password_hash
from services.api.app.config import Config, get_config
from services.api.app.config import get_config as get_app_settings


@pytest_asyncio.fixture
async def app(db_pool) -> FastAPI:
    """Настроенное приложение FastAPI для тестов"""
    # Устанавливаем тестовый конфиг
    from services.api.app.main import app as fastapi_app

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
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(
        base_url="http://test/api/v1",
        headers={"Content-Type": "application/json"},
        transport=transport,
    ) as ac:
        yield ac


@pytest.fixture(scope="session")
def config() -> Config:
    return get_config()


@pytest_asyncio.fixture
async def user_login_fixture(
    user_factory,
    client: AsyncClient,
) -> dict:
    plain_password = "password"
    user = await user_factory(
        email="email@mail.ru",
        password=get_password_hash(plain_password),
        username="username",
    )

    response = await client.post(
        "users/login-user",
        json={
            "email": user.email,
            "password": plain_password,
        },
    )

    response_json = response.json()
    yield response_json
