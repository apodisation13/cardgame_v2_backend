import logging

from lib.utils.events import event_sender
from lib.utils.events.event_types import EventType
from lib.utils.tasks.base import TaskBase


logger = logging.getLogger(__name__)


class TaskOne(TaskBase):
    name = "task_one"

    async def do(self):
        logger.info("Starting TaskOne execution")
        print(111)
        print(222)

        async with self.db.connection() as conn:
            users = await conn.fetch("SELECT * FROM users")
            logger.info("Total tasks in database: %s", len(users))

        await event_sender.create_event(
            event_type=EventType.EVENT_1,
            payload={"users": dict(users[0]) if users else []},
            config=self.config,
        )

        logger.info("TaskOne completed successfully")
