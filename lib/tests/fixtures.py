import logging.config
import os
import sys
from collections.abc import AsyncGenerator
import threading

import asyncpg
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from lib.utils.config.base import BaseConfig, get_config
from lib.utils.config.env_types import EnvType
from lib.utils.db.pool import Database
from lib.utils.models import Base


logger = logging.getLogger(__name__)
logging.config.dictConfig(BaseConfig.LOGGING)


_db_setup_lock = threading.Lock()
_db_setup_done = False


@pytest.fixture(autouse=True, scope="session")
def setup_tests_config():
    os.environ["CONFIG"] = EnvType.TEST_LOCAL
    logger.info("!!!!!!!!!!STR14 SET CONFIG")


@pytest.fixture(scope="session")
def config() -> BaseConfig:
    return get_config()


def check_test_db_name(
    config: BaseConfig,
) -> None:
    if not config.DB_NAME.startswith("test_"):
        raise Exception("Can not use db without test_ prefix in tests")


async def check_db_connection(
    config: BaseConfig,
) -> None:
    logger.info("🔧 Setting up database...")
    try:
        conn = await asyncpg.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME
        )
        await conn.close()
        logger.info(f"✅ Connected to test database '{config.DB_NAME}'")
    except asyncpg.InvalidCatalogNameError:
        raise Exception("Can not connect to test database")


async def apply_migrations(
    config: BaseConfig,
) -> None:
    engine = create_async_engine(config.DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Tables created, migrations applied")
    await engine.dispose()


async def teardown_db(
    config: BaseConfig,
) -> None:
    global _db_setup_done

    # Очистка в конце
    with _db_setup_lock:
        if _db_setup_done:
            print()
            logger.info("🧹 Cleaning up database...")
            engine = create_async_engine(config.DB_URL, echo=False)
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                logger.info("✅ Tables dropped")
            await engine.dispose()
            _db_setup_done = False


async def create_pool(
    config: BaseConfig,
) -> asyncpg.pool.Pool:
    logger.info("🔌 Creating NEW connection pool...")
    db_pool = await asyncpg.create_pool(
        dsn=config.DB_URL.replace("postgresql+asyncpg://", "postgresql://"),
        min_size=1,
        max_size=10,
        command_timeout=60
    )
    logger.info("✅ Connection pool created")
    return db_pool


async def clean_data(pool: asyncpg.pool.Pool) -> None:
    async with pool.acquire() as conn:
        tables = await conn.fetch(
            """
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            """
        )
        if tables:
            await conn.execute('SET session_replication_role = replica;')
            for table in tables:
                await conn.execute(f'TRUNCATE TABLE "{table["tablename"]}" CASCADE')
            await conn.execute('SET session_replication_role = DEFAULT;')
            logger.info("✅ Data cleaned")


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def setup_database(config):
    check_test_db_name(config)

    global _db_setup_done
    with _db_setup_lock:
        if not _db_setup_done:
            await check_db_connection(config)
            await apply_migrations(config)
            _db_setup_done = True
        else:
            logger.info("♻️ Database already setup")

    yield

    await teardown_db(config)


@pytest_asyncio.fixture
async def db_pool(
    setup_database,
    config,
) -> AsyncGenerator[asyncpg.Pool, None]:
    _db_pool = await create_pool(config)
    yield _db_pool

    await clean_data(_db_pool)

    await _db_pool.close()
    logger.info("✅ Connection pool closed")


@pytest_asyncio.fixture
async def db_connection(
    db_pool,
) -> AsyncGenerator[asyncpg.Connection, None]:
    async with db_pool.acquire() as conn:
        yield conn


@pytest_asyncio.fixture
async def db():
    db_ = Database()
    yield db_
