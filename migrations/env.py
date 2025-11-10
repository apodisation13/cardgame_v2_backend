import asyncio
import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context

# Добавляем корень проекта в PYTHONPATH
import sys

from lib.utils.config.base import BaseConfig

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lib.utils.models import *  # Импортируем все модели

load_dotenv()

config = context.config

# Переопределяем URL из alembic.ini нашим конфигом
config.set_main_option("sqlalchemy.url", BaseConfig.DB_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    """Запуск миграций в offline режиме"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    """Запуск миграций в online режиме"""
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())