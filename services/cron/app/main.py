import asyncio
from contextlib import asynccontextmanager
import logging.config
import os
import signal
import sys
from types import FrameType

from lib.utils.elk.elastic_logger import ElasticLoggerManager


# Добавляем корневую директорию проекта в Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))


from lib.utils.db.pool import Database
from lib.utils.tasks.base import TaskScheduler
from services.cron.app.config import get_config

# Импортируем задачи
from tasks import TASKS


class Application:
    def __init__(self):
        self.config = get_config()
        self.db = Database(self.config)

        self.scheduler = TaskScheduler(config=self.config, db=self.db)
        self.running = False

        logging.config.dictConfig(self.config.LOGGING)

        elastic_logger_manager = ElasticLoggerManager()
        elastic_logger_manager.initialize(
            config=self.config,
            service_name="cron",
            delay_seconds=5,
        )

        logger = logging.getLogger(__name__)
        self.logger = logger

    async def startup(self):
        """Инициализация приложения"""
        self.logger.info("Starting Cron Application with APScheduler")

        # Подключаемся к БД
        await self.db.connect()
        self.logger.info("Database connected")

        # Регистрируем задачи
        for task in TASKS:
            self.scheduler.register_task(task)

        # Запускаем планировщик
        await self.scheduler.start()

        # Настройка обработчиков сигналов
        self._setup_signal_handlers()

        self.running = True
        self.logger.info("Application started successfully")

    async def shutdown(self):
        """Корректное завершение приложения"""
        self.logger.info("Shutting down application")
        self.running = False
        self.scheduler.stop()
        await self.db.disconnect()
        self.logger.info("Application shutdown complete")

    def _setup_signal_handlers(self):
        """Настройка обработчиков сигналов для graceful shutdown"""

        def signal_handler(
            signum: int,
            frame: FrameType,
        ):
            self.logger.info("Received signal %s, initiating shutdown", signum)
            asyncio.create_task(self.shutdown())  # noqa: RUF006

        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

    async def run(self):
        """Основной цикл приложения"""
        await self.startup()

        try:
            # Демонстрационная информация о запланированных задачах
            jobs = self.scheduler.get_scheduled_jobs()
            self.logger.info("Scheduled jobs:")
            for job in jobs:
                self.logger.info("  - %s: next run at %s}", job["name"], job["next_run"])

            # Основной цикл ожидания
            while self.running:
                await asyncio.sleep(2)

        except Exception as e:
            self.logger.error("Application error: %s", e)
        finally:
            if self.running:
                await self.shutdown()


@asynccontextmanager
async def lifespan():
    """Context manager для управления жизненным циклом"""
    app = Application()
    try:
        await app.startup()
        yield app
    finally:
        await app.shutdown()


async def main() -> None:
    """Основная точка входа"""
    app = Application()
    try:
        await app.run()
    except KeyboardInterrupt:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
