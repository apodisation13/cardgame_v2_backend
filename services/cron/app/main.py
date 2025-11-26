import asyncio
import os
import signal
import logging.config
import sys
import time
from contextlib import asynccontextmanager


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
        logger = logging.getLogger(__name__)
        logging.config.dictConfig(self.config.LOGGING)
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

        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating shutdown")
            asyncio.create_task(self.shutdown())

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
                self.logger.info(f"  - {job['name']}: next run at {job['next_run']}")

            # Основной цикл ожидания
            while self.running:
                # print("STR88, sleeping...")
                await asyncio.sleep(2)

                # Пример: перезагрузка задач каждые 5 минут
                # if int(time.time()) % 300 == 0:
                #     await self.scheduler.reload_tasks()

        except Exception as e:
            self.logger.error(f"Application error: {e}")
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


async def main():
    """Основная точка входа"""
    app = Application()
    try:
        await app.run()
    except KeyboardInterrupt:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
