from contextlib import asynccontextmanager

import asyncpg

from lib.utils.config.base import config


class Database:
    def __init__(self):
        self.pool = None

    async def connect(self) -> asyncpg.Pool:
        """Создание пула подключений"""
        print("STR14, connect to db")
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                dsn=config.DB_URL,
                min_size=1,
                max_size=10,
                command_timeout=60,
            )
        print("STR22!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return self.pool

    async def disconnect(self) -> None:
        """Закрытие пула подключений"""
        if self.pool:
            await self.pool.close()
            self.pool = None

    @asynccontextmanager
    async def connection(self):
        """Контекстный менеджер для одного подключения"""
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


# Глобальный инстанс БД
db = Database()
