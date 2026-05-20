import logging

from lib.utils.events.event_processor import EventProcessor
from lib.utils.events.event_types import EventProcessingActionStatus
from lib.utils.tasks.base import TaskBase


logger = logging.getLogger(__name__)

MAX_RETRY_COUNT = 3


class TaskResendEvents(TaskBase):
    name = "task_resend_events"

    async def do(self):
        async with self.db.connection() as connection:
            failed_events: list[dict] = await connection.fetch(
                """
                SELECT
                    id,
                    type,
                    payload,
                    actions_log
                FROM
                    event_log
                WHERE
                    state = $1
                    AND retry_count < $2
                """,
                EventProcessingActionStatus.FAILED,
                MAX_RETRY_COUNT,
            )

        if not failed_events:
            logger.info("No failed events to retry")
            return

        logger.info("Found %d failed events to retry", len(failed_events))

        for record in failed_events:
            await self._retry_event(record)

    async def _retry_event(
        self,
        record: dict,
    ) -> None:
        event_id = record["id"]

        async with self.db.connection() as connection:
            await connection.execute(
                """
                UPDATE
                    event_log
                SET
                    retry_count = retry_count + 1,
                    updated_at = NOW()
                WHERE
                    id = $1
                """,
                event_id,
            )

        logger.info("Retrying event %s (type=%s)", event_id, record["type"])

        processor = EventProcessor(
            db=self.db,
            config=self.config,
        )
        await processor.retry_failed_actions(
            event_id=event_id,
            event_type=record["type"],
            payload=record["payload"],
            actions_log=record["actions_log"],
        )
