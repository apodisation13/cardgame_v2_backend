#!/usr/bin/env python3
import logging.config
import os
from pathlib import Path
import subprocess
import sys

from lib.utils.elk.elastic_logger import ElasticLoggerManager

# Добавляем корневую директорию проекта в Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from services.migrant.app.config import get_config


config = get_config()
logging.config.dictConfig(config.LOGGING)

elastic_logger_manager = ElasticLoggerManager()
elastic_logger_manager.initialize(
    config=config,
    service_name="migrant",
    delay_seconds=5,
)

logger = logging.getLogger(__name__)


def run_migrations() -> bool:
    try:
        logger.info("Запуск миграций базы данных...")

        # Путь к alembic.ini
        app_dir = Path(__file__).parent
        alembic_ini_path = app_dir / "alembic.ini"

        if not alembic_ini_path.exists():
            logger.error("Файл alembic.ini не найден: %s", alembic_ini_path)
            return False

        logger.info("Применение миграций...")

        # Используем subprocess для большего контроля
        result = subprocess.run(  # noqa: S603
            [sys.executable, "-m", "alembic", "-c", str(alembic_ini_path), "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd=str(app_dir),
        )

        # Выводим результаты
        if result.stdout:
            logger.info("STDOUT: %s", result.stdout)
        if result.stderr:
            logger.info("STDERR: %s", result.stderr)

        if result.returncode == 0:
            logger.info("Миграции успешно выполнены")
            return True
        else:
            logger.error("Ошибка выполнения миграций, код возврата: %s", result.returncode)
            return False

    except Exception as e:
        logger.error("Ошибка при выполнении миграций: %s", e)
        return False


def main():
    """Основная функция"""
    logger.info("Запуск сервиса миграций")

    success = run_migrations()

    if success:
        logger.info("Сервис миграций завершил работу успешно")
        sys.exit(0)
    else:
        logger.error("Сервис миграций завершил работу с ошибкой")
        sys.exit(1)


if __name__ == "__main__":
    main()
