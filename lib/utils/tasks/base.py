import abc
import asyncio
import logging
import time
from typing import Any

from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
# from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, EVENT_JOB_MISSED
from lib.utils.config.base import BaseConfig
from lib.utils.db.pool import Database


logger = logging.getLogger(__name__)


class TaskBase(abc.ABC):
    name: str = "base_task"

    def __init__(
        self,
        config: BaseConfig,
        db: Database,
    ):
        self.config = config
        self.db = db

    @abc.abstractmethod
    async def do(self):
        pass


class TaskScheduler:
    def __init__(
        self,
        config: BaseConfig,
        db: Database,
    ):
        self.config = config
        self.db = db
        self.tasks: dict[str, Any] = {}

        self.last_reload_time = 0
        self.reload_interval = 60
        self._scheduled_task_ids: set[str] = set()  # ID задач в планировщике

        # Настройка APScheduler
        jobstores = {
            "default": MemoryJobStore()  # или SQLAlchemyJobStore для персистентности
        }

        job_defaults = {
            "coalesce": True,  # объединять пропущенные выполнения
            "max_instances": 1,  # только один экземпляр задачи одновременно
            "misfire_grace_time": 60,  # 60 секунд на выполнение пропущенной задачи
        }

        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            job_defaults=job_defaults,
            timezone="UTC",
        )

        # # Подписка на события
        # self.scheduler.add_listener(self._job_executed, EVENT_JOB_EXECUTED)
        # self.scheduler.add_listener(self._job_error, EVENT_JOB_ERROR)
        # self.scheduler.add_listener(self._job_missed, EVENT_JOB_MISSED)

    def register_task(
        self,
        task_class: TaskBase,
    ) -> None:
        """Регистрирует класс задачи"""
        self.tasks[task_class.name] = task_class
        logger.info("Registered task: %s", task_class.name)

    async def start(self) -> None:
        """Запуск планировщика"""
        logger.info("Starting APScheduler")
        await self._load_tasks_from_db()
        self.scheduler.start()

        # Запускаем фонтовую задачу для проверки изменений
        asyncio.create_task(self._periodic_reload_check())  # noqa: RUF006

    async def _get_active_tasks(self) -> list:
        async with self.db.connection() as conn:
            active_tasks = await conn.fetch("""SELECT * FROM cron_tasks WHERE is_active is TRUE""")
            print("LEN(active_tasks)", len(active_tasks))
            print("active_tasks", active_tasks)
        return active_tasks

    async def _load_tasks_from_db(self) -> None:
        """Загрузка активных задач из базы данных"""
        active_tasks = await self._get_active_tasks()

        for task_record in active_tasks:
            task_name = task_record["name"]
            task_id = task_record["id"]
            schedule = task_record["schedule"]
            print(98, task_name, task_id, schedule)

            if task_name in self.tasks:
                await self._schedule_task(task_id, task_name, schedule)
            else:
                logger.warning("Unknown task '%s' found in database", task_name)

    async def _execute_task(
        self,
        task_class: type[TaskBase],
        task_name: str,
    ):
        """Выполняет задачу с обработкой ошибок и логированием"""
        task_instance = task_class(self.config, self.db)

        try:
            logger.info("Starting execution of task: %s", task_name)
            await task_instance.do()
            logger.info("Task %s completed successfully", task_name)

        except Exception as e:
            logger.error("Task %s failed: %s", task_name, str(e))

    # def _job_executed(self, event):
    #     """Обработчик успешного выполнения задачи"""
    #     if event.job_id.startswith('task_'):
    #         logger.debug(f"Job {event.job_id} executed successfully")
    #
    # def _job_error(self, event):
    #     """Обработчик ошибок выполнения задачи"""
    #     if event.job_id.startswith('task_'):
    #         logger.error(f"Job {event.job_id} failed with exception: {event.exception}")
    #
    # def _job_missed(self, event):
    #     """Обработчик пропущенных задач"""
    #     if event.job_id.startswith('task_'):
    #         logger.warning(f"Job {event.job_id} was missed")

    def stop(self) -> None:
        """Останавливает планировщик"""
        self.scheduler.shutdown(wait=False)

    def get_scheduled_jobs(self) -> list:
        """Возвращает информацию о запланированных задачах"""
        return [
            {"id": job.id, "name": job.name, "next_run": job.next_run_time, "trigger": str(job.trigger)}
            for job in self.scheduler.get_jobs()
        ]

    async def _periodic_reload_check(self) -> None:
        """Периодическая проверка необходимости перезагрузки задач"""
        while True:
            try:
                await asyncio.sleep(60)  # Проверяем каждую минуту
                await self.reload_tasks()

            except Exception as e:
                logger.error("Error in periodic reload check: %s", str(e))
                await asyncio.sleep(300)  # Ждем 5 минут при ошибке

    async def reload_tasks(self) -> None:
        """Перезагружает задачи из базы данных"""
        logger.info("Reloading tasks from database!!!!!!!!!!!!!!!!!!!!!!!")

        try:
            db_tasks = await self._get_active_tasks()

            # Создаем множество ID активных задач из БД
            db_task_ids = {f"task_{task['id']}" for task in db_tasks}

            # Удаляем задачи, которых нет в БД или которые неактивны
            for job in self.scheduler.get_jobs():
                if job.id.startswith("task_"):
                    if job.id not in db_task_ids:
                        job.remove()
                        logger.info("Removed task: %s, (id %s)", job.name, job.id)

            # Добавляем/обновляем задачи из БД
            for task_record in db_tasks:
                task_name = task_record["name"]
                task_id = task_record["id"]
                schedule = task_record["schedule"]

                if task_name in self.tasks:
                    await self._schedule_task(task_id, task_name, schedule)

            self.last_reload_time = time.time()
            logger.info("Tasks reloaded successfully")

        except Exception as e:
            logger.error("Failed to reload tasks: %s", e)

    async def _schedule_task(
        self,
        task_id: int,
        task_name: str,
        schedule: str,
    ) -> None:
        """Добавляет или обновляет задачу в планировщике"""
        try:
            task_class = self.tasks[task_name]
            job_id = f"task_{task_id}"

            # Проверяем, существует ли уже задача
            existing_job = self.scheduler.get_job(job_id)

            if existing_job:
                # Если расписание изменилось - обновляем
                current_trigger = str(existing_job.trigger)
                new_trigger = str(CronTrigger.from_crontab(schedule))

                if current_trigger != new_trigger:
                    existing_job.reschedule(trigger=CronTrigger.from_crontab(schedule))
                    logger.info("Rescheduled task %s with new schedule: %s", task_name, schedule)
            else:
                # Добавляем новую задачу
                self.scheduler.add_job(
                    self._execute_task,
                    trigger=CronTrigger.from_crontab(schedule),
                    args=[task_class, task_id, task_name],
                    id=job_id,
                    name=task_name,
                    replace_existing=True,
                )

        except Exception as e:
            logger.error("Failed to schedule task '%s': %s", task_name, e)
