from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from services.ws.app.apps.matchmaking.routes import router


@pytest.fixture(autouse=True)
def reset_manager():
    """Сбрасываем состояние менеджера перед каждым тестом."""
    from services.ws.app.apps.matchmaking.manager import manager

    manager._waiting = None
    manager._rooms.clear()
    manager._player_rooms.clear()
    yield


@pytest.fixture
def app() -> FastAPI:
    """
    Минимальное FastAPI приложение для тестов — без lifespan и реальной БД.
    Конфиг и DB замоканы, поэтому CONFIG env var не нужен.
    """
    test_app = FastAPI()
    test_app.include_router(router)

    mock_config = MagicMock()
    mock_config.USER_PASSWORD_SECRET_KEY = "test-secret"
    mock_config.ALGORITHM = "HS256"

    test_app.state.config = mock_config
    test_app.state.db = AsyncMock()
    return test_app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    with TestClient(app) as c:
        yield c
