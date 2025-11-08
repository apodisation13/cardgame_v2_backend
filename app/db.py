import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base


load_dotenv()

# Используем asyncpg для PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db").replace(
    "postgresql://", "postgresql+asyncpg://"
)

# Асинхронный engine
engine = create_async_engine(
    DATABASE_URL,
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

Base = declarative_base()

async def get_db():
    """Асинхронная зависимость для получения сессии БД"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def create_tables():
    """Создание таблиц (для тестов и инициализации)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_tables():
    """Удаление таблиц (для тестов)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
