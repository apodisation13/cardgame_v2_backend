import json
import logging
from uuid import UUID

from lib.utils.config.base import BaseConfig
from lib.utils.db.pool import Database
from lib.utils.events.actions import ACTION_REGISTRY
from lib.utils.events.event_types import EventProcessingState, EventType
from lib.utils.schemas.events import ActionConfigData, EventMessage


logger = logging.getLogger(__name__)


class EventProcessor:
    def __init__(
        self,
        db: Database,
        config: BaseConfig,
    ):
        self.db = db
        self.config = config

    async def process_event(
        self,
        event_message: EventMessage,
    ):
        event_type: EventType = event_message.event_type
        payload: dict = event_message.payload
        print("STR24", event_type, payload)

        await self._update_processing_state(
            event_id=event_message.id,
            state=EventProcessingState.IN_PROGRESS,
        )

        async with self.db.connection() as conn:
            event_config = await conn.fetchrow(
                """select processing::jsonb from events where type = $1""",
                event_type,
            )

            processing: list[ActionConfigData] = [
                ActionConfigData(
                    type=item["type"],
                    conditions=item["conditions"],
                    receiver=item["receiver"],
                )
                for item in json.loads(event_config["processing"])
            ]

        if not event_config:
            raise ValueError(f"Event config not found for {event_type}")

        try:
            for action_config_data in processing:
                await self._execute_action(
                    action_config=action_config_data,
                    payload=payload,
                )

        except Exception:
            logger.error("Failed to process %s", event_type)
            await self._update_processing_state(
                event_id=event_message.id,
                state=EventProcessingState.FAILED,
            )
            return

        await self._update_processing_state(
            event_id=event_message.id,
            state=EventProcessingState.SUCCESS,
        )

    async def _execute_action(
        self,
        action_config: ActionConfigData,
        payload: dict,
    ) -> None:
        action_class = ACTION_REGISTRY.get(action_config.type)

        if not action_class:
            raise ValueError(f"Unknown action type: {action_config.type}")

        action_instance = action_class(
            config=self.config,
            action_config=action_config,
            payload=payload,
        )

        try:
            if action_instance.check_conditions():
                await action_instance.execute(payload=payload)
            else:
                print("failed conditions")
        except RuntimeError as e:
            raise Exception(f"Action {action_class} execution failed") from e

    async def _update_processing_state(
        self,
        event_id: UUID,
        state: EventProcessingState,
    ) -> None:
        async with self.db.connection() as connection:
            await connection.execute(
                """
                UPDATE event_log
                SET state = $2
                WHERE id = $1
                """,
                event_id,
                state,
            )
