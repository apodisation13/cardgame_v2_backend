import logging

from lib.utils.events import event_sender
from lib.utils.events.event_types import EventType
from lib.utils.tasks.base import TaskBase


logger = logging.getLogger(__name__)


class TaskOne(TaskBase):
    name = "task_one"

    async def do(self):
        logger.info("Starting TaskOne execution")

        print("STR15", type(self.db))

        async with self.db.connection() as conn:
            users = await conn.fetch("SELECT * FROM users")
            logger.info(f"Total tasks in database: {len(users)}")

        await event_sender.event(
            event_type=EventType.EVENT_1,
            payload={"users": users[0]},
            config=self.config,
        )

        logger.info("TaskOne completed successfully")
