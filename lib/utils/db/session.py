from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from lib.utils.config.base import BaseConfig
from lib.utils.models.base import Base


# Асинхронный engine
engine = create_async_engine(
    BaseConfig.DB_URL,
    echo=False,  # Логирование SQL запросов (можно включить для дебага)
    future=True,
    pool_pre_ping=True  # Проверка соединения перед использованием
)


# Асинхронная сессия
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

async def get_db_session():
    """Dependency для получения async сессии"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def create_tables():
    """Создание таблиц (для тестов)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_tables():
    """Удаление таблиц (для тестов)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
