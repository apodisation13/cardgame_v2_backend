import asyncio
from collections.abc import AsyncGenerator
import os

import asyncpg
import pytest

import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine


# Переопределяем конфиг для тестов
os.environ["CONFIG"] = "test_local"


from lib.utils.config.base import config
from lib.utils.models import Base  # Ваш базовый класс для моделей


@pytest.fixture(scope="session")
def event_loop():
    """Создаем event loop для всей тестовой сессии"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def setup_database():
    """Настройка БД для тестов - простая версия"""

    # Проверяем/создаем БД
    try:
        conn = await asyncpg.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME
        )
        await conn.close()
        print(f"\n✅ Connected to test database '{config.DB_NAME}'")
    except asyncpg.InvalidCatalogNameError:
        pass

    # Создаем все таблицы через SQLAlchemy
    engine = create_async_engine(
        config.DB_URL,
        echo=False  # Поставьте True для отладки SQL
    )

    async with engine.begin() as conn:
        # Удаляем все таблицы
        await conn.run_sync(Base.metadata.drop_all)
        # Создаем все таблицы
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables created")
        print(Base.metadata, Base.metadata.tables)

    await engine.dispose()

    yield

    # После всех тестов можно очистить таблицы (опционально)
    engine = create_async_engine(
        config.DB_URL,
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("✅ Tables dropped")
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def db_pool(setup_database) -> AsyncGenerator[asyncpg.Pool, None]:
    """Создание пула подключений для всей сессии"""
    pool = await asyncpg.create_pool(
        dsn=config.DB_URL.replace("postgresql+asyncpg://", "postgresql://"),
        # dsn=config.DB_URL,
        min_size=1,
        max_size=10,
        command_timeout=60
    )
    print("✅ Connection pool created")

    yield pool

    await pool.close()
    print("✅ Connection pool closed")


@pytest_asyncio.fixture(autouse=True)
async def clean_data(db_pool):
    """Автоматическая очистка данных после каждого теста"""
    yield

    async with db_pool.acquire() as conn:
        # Получаем список всех таблиц (кроме системных)
        tables = await conn.fetch(
            """
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
            """
        )

        if tables:
            # Отключаем проверку внешних ключей
            await conn.execute('SET session_replication_role = replica;')

            # Очищаем каждую таблицу
            for table in tables:
                await conn.execute(f'TRUNCATE TABLE "{table["tablename"]}" CASCADE')

            # Включаем обратно проверку внешних ключей
            await conn.execute('SET session_replication_role = DEFAULT;')

            print("\n✅ Data cleaned")


@pytest_asyncio.fixture
async def db_connection(db_pool) -> AsyncGenerator[asyncpg.Connection, None]:
    """Подключение для каждого теста"""
    async with db_pool.acquire() as conn:
        yield conn
