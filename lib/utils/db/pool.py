import asyncpg

from lib.utils.config.base import BaseConfig


class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        """Создание пула подключений"""
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                dsn=BaseConfig.DB_URL,  # ← Используем как есть!
                min_size=1,
                max_size=10,
                command_timeout=60
            )
        return self.pool

    async def disconnect(self):
        """Закрытие пула подключений"""
        if self.pool:
            await self.pool.close()
            self.pool = None

    # async def execute(self, query: str, *args):
    #     """Выполнение запроса"""
    #     async with self.pool.acquire() as connection:
    #         return await connection.execute(query, *args)
    #
    # async def fetch(self, query: str, *args):
    #     """Получение нескольких записей"""
    #     async with self.pool.acquire() as connection:
    #         return await connection.fetch(query, *args)
    #
    # async def fetchrow(self, query: str, *args):
    #     """Получение одной записи"""
    #     async with self.pool.acquire() as connection:
    #         return await connection.fetchrow(query, *args)
    #
    # async def fetchval(self, query: str, *args):
    #     """Получение значения"""
    #     async with self.pool.acquire() as connection:
    #         return await connection.fetchval(query, *args)

# Глобальный инстанс БД
db = Database()
