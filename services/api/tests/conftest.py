import pytest

from services.api.app.apps.db import Base, get_db
from services.api.app.apps.main import app
from services.api.app.apps.models import User
from httpx import AsyncClient
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from services.api.tests.factories import UserFactory


# Тестовая база данных в памяти (SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Фикстура для event loop"""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Асинхронная сессия для тестов"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True
    )

    # Создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session

    # Удаляем таблицы после теста
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """Асинхронный тестовый клиент"""

    async def override_get_db():
        try:
            yield db_session
        finally:
            await db_session.close()

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_users(db_session: AsyncSession) -> list[User]:
    """Создает несколько тестовых пользователей через фабрику"""
    users = UserFactory.build_batch(3)

    for user in users:
        db_session.add(user)

    await db_session.commit()

    # Refresh всех пользователей чтобы получить их ID
    for user in users:
        await db_session.refresh(user)

    return users


@pytest_asyncio.fixture
async def single_user(db_session: AsyncSession) -> User:
    """Создает одного тестового пользователя через фабрику"""
    user = UserFactory.build(
        name="Test User",
        email="test@example.com"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user
