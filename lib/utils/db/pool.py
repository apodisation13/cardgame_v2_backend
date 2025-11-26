from contextlib import asynccontextmanager

import asyncpg
import logging

from lib.utils.config.base import get_config


logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.pool = None
        self.config = get_config()

    async def connect(self) -> asyncpg.Pool:
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                dsn=self.config.DB_URL,
                min_size=1,
                max_size=10,
                command_timeout=60,
            )
        logger.info("Connected to db")
        return self.pool

    async def disconnect(self) -> None:
        if self.pool:
            await self.pool.close()
            self.pool = None

    @asynccontextmanager
    async def connection(self):
        if not self.pool:
            await self.connect()

        async with self.pool.acquire() as conn:
            yield conn

    @asynccontextmanager
    async def transaction(self):
        """Контекстный менеджер для транзакции"""
        async with self.connection() as conn:
            async with conn.transaction():
                yield conn
