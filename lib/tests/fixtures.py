from collections.abc import AsyncGenerator
import logging.config
import os
import threading
from unittest.mock import AsyncMock, patch

import asyncpg
import pytest

from lib.utils.config.base import BaseConfig, BaseTestLocalConfig, get_config
from lib.utils.config.env_types import EnvType
from lib.utils.db.pool import Database
from lib.utils.events.event_processor import EventProcessor
from lib.utils.models import Base
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine


logger = logging.getLogger(__name__)
logging.config.dictConfig(BaseConfig.LOGGING)


_db_setup_lock = threading.Lock()
_db_setup_done = False


@pytest.fixture(autouse=True, scope="session")
def setup_tests_config():
    os.environ["CONFIG"] = EnvType.TEST_LOCAL
    logger.info("Setting up test config")


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
            database=config.DB_NAME,
        )
        await conn.close()
        logger.info("✅ Connected to test database  %s", config.DB_NAME)
    except asyncpg.InvalidCatalogNameError as e:
        raise Exception("Can not connect to test database") from e


async def apply_migrations(
    config: BaseTestLocalConfig,
) -> None:
    engine = create_async_engine(config.DB_URL_SQL_ALCHEMY, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Tables created, migrations applied")
    await engine.dispose()


async def teardown_db(
    config: BaseTestLocalConfig,
) -> None:
    global _db_setup_done

    # Очистка в конце
    with _db_setup_lock:
        if _db_setup_done:
            print()
            logger.info("🧹 Cleaning up database...")
            engine = create_async_engine(config.DB_URL_SQL_ALCHEMY, echo=False)
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                logger.info("✅ Tables dropped")
            await engine.dispose()
            _db_setup_done = False


async def create_pool(
    config: BaseTestLocalConfig,
) -> asyncpg.pool.Pool:
    logger.info("🔌 Creating NEW connection pool...")
    db = Database(config)
    db_pool = await db.connect()
    logger.info("✅ Connection pool created")
    return db_pool


async def clean_data(pool: asyncpg.pool.Pool) -> None:
    async with pool.acquire() as conn:
        tables = await conn.fetch(
            """
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            """,
        )
        if tables:
            await conn.execute("SET session_replication_role = replica;")
            for table in tables:
                await conn.execute(f'TRUNCATE TABLE "{table["tablename"]}" RESTART IDENTITY CASCADE')
            await conn.execute("SET session_replication_role = DEFAULT;")
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
async def db(
    config: BaseTestLocalConfig,
):
    db_ = Database(config)
    yield db_
    await db_.disconnect()


@pytest.fixture
def event_sender_mock():
    with patch("lib.utils.events.event_sender.create_event", new_callable=AsyncMock) as mock:
        mock.return_value = True
        yield mock


@pytest.fixture
def processor(db, config):
    return EventProcessor(db=db, config=config)


@pytest_asyncio.fixture
async def event_processor_fixture(db_pool):
    import uuid

    from lib.utils.db.pool import Database
    from lib.utils.events.event_processor import EventProcessor
    from lib.utils.schemas.events import EventMessage

    async def _run_processor(event_type, payload, config):
        db = Database(config)
        db.pool = db_pool
        event = EventMessage(id=uuid.uuid4(), event_type=event_type, payload=payload)
        processor = EventProcessor(config=config, db=db)
        await processor.process_event(event)

    with patch("lib.utils.events.event_sender.create_event", side_effect=_run_processor):
        yield
