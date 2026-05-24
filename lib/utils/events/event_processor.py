import logging
from uuid import UUID

from lib.utils.config.base import BaseConfig
from lib.utils.db.pool import Database
from lib.utils.events.actions import ACTION_REGISTRY
from lib.utils.events.event_types import EventProcessingActionStatus, EventProcessingState, EventType
from lib.utils.schemas.events import ActionConfigData, ActionContext, EventMessage


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

        await self._update_processing_state(
            event_id=event_message.id,
            state=EventProcessingState.IN_PROGRESS,
        )

        try:
            event_config = await self._get_event_config(
                event_type=event_type,
            )

            if not event_config:
                raise ValueError(f"Event config not found for {event_type}")

            processing: list[ActionConfigData] = [
                ActionConfigData(
                    type=item["type"],
                    conditions=item["conditions"],
                    receiver=item.get("receiver"),
                    message=item.get("message"),
                )
                for item in event_config["processing"]
            ]

        except Exception as e:
            logger.error("Failed to load event config for %s: %s", event_type, e)
            await self._finalize_event(
                event_id=event_message.id,
                state=EventProcessingState.FAILED,
                actions_log=[
                    {
                        "type": "config",
                        "state": EventProcessingActionStatus.FAILED,
                        "error": str(e),
                    },
                ],
            )
            return

        actions_log = await self._run_actions(
            processing=processing,
            payload=payload,
            event_type=event_type,
        )

        final_state = (
            EventProcessingState.SUCCESS
            if all(a["state"] != EventProcessingActionStatus.FAILED for a in actions_log)
            else EventProcessingState.FAILED
        )
        await self._finalize_event(
            event_id=event_message.id,
            state=final_state,
            actions_log=actions_log,
        )

    async def retry_failed_actions(
        self,
        event_id: UUID,
        event_type: EventType,
        payload: dict,
        actions_log: list[dict],
    ) -> None:
        failed_types = {a["type"] for a in actions_log if a["state"] == EventProcessingActionStatus.FAILED}

        event_config = await self._get_event_config(
            event_type=event_type,
        )

        if not event_config:
            logger.error("Event config not found for %s during retry", event_type)
            return

        processing = [
            ActionConfigData(
                type=item["type"],
                conditions=item["conditions"],
                receiver=item.get("receiver"),
                message=item.get("message"),
            )
            for item in event_config["processing"]
            if item["type"] in failed_types
        ]

        updated_log = [dict(entry) for entry in actions_log]
        for action_config_data in processing:
            try:
                status: EventProcessingActionStatus = await self._execute_action(
                    action_config=action_config_data,
                    payload=payload,
                    event_type=event_type,
                )

                for entry in updated_log:
                    if entry["type"] == action_config_data.type:
                        entry["state"] = status
                        entry.pop("error", None)
            except Exception as e:
                logger.error("Retry failed for action %s: %s", action_config_data.type, e)
                for entry in updated_log:
                    if entry["type"] == action_config_data.type:
                        entry["error"] = str(e)

        final_state = (
            EventProcessingState.SUCCESS
            if all(a["state"] != EventProcessingActionStatus.FAILED for a in updated_log)
            else EventProcessingState.FAILED
        )
        await self._finalize_event(
            event_id=event_id,
            state=final_state,
            actions_log=updated_log,
        )

    async def _get_event_config(
        self,
        event_type: EventType,
    ) -> dict:
        async with self.db.connection() as connection:
            event_config: dict = await connection.fetchrow(
                """
                    SELECT
                        processing::jsonb
                    FROM
                        events
                    WHERE
                        type = $1
                """,
                event_type,
            )

        logger.info("Got config %s for event %s", event_config, event_type)
        return event_config

    async def _run_actions(
        self,
        processing: list[ActionConfigData],
        payload: dict,
        event_type: EventType,
    ) -> list[dict]:
        actions_log = []
        for action_config_data in processing:
            try:
                status: EventProcessingActionStatus = await self._execute_action(
                    action_config=action_config_data,
                    payload=payload,
                    event_type=event_type,
                )
                actions_log.append(
                    {
                        "type": action_config_data.type,
                        "state": status,
                    },
                )
            except Exception as e:
                logger.error("Action %s failed: %s", action_config_data.type, e)
                actions_log.append(
                    {
                        "type": action_config_data.type,
                        "state": EventProcessingActionStatus.FAILED,
                        "error": str(e),
                    },
                )
        return actions_log

    async def _execute_action(
        self,
        action_config: ActionConfigData,
        payload: dict,
        event_type: EventType,
    ) -> EventProcessingActionStatus:
        action_class = ACTION_REGISTRY.get(action_config.type)

        if not action_class:
            raise ValueError(f"Unknown action type: {action_config.type}")

        context = ActionContext(
            event_type=event_type,
            payload=payload,
            action_config=action_config,
        )
        action_instance = action_class(
            config=self.config,
            context=context,
            db=self.db,
        )

        try:
            if action_instance.check_conditions():
                logger.info("Executing action %s", action_instance)
                await action_instance.execute()
                logger.info("Action %s marked as success", action_instance)
                return EventProcessingActionStatus.SUCCESS
            else:
                return EventProcessingActionStatus.CONDITIONS_FALSE
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
                UPDATE
                    event_log
                SET
                    state = $2,
                    updated_at = NOW()
                WHERE id = $1
                """,
                event_id,
                state,
            )

    async def _finalize_event(
        self,
        event_id: UUID,
        state: EventProcessingState,
        actions_log: list[dict],
    ) -> None:
        async with self.db.connection() as connection:
            await connection.execute(
                """
                UPDATE
                    event_log
                SET
                    state = $2,
                    actions_log = $3,
                    updated_at = NOW()
                WHERE
                    id = $1
                """,
                event_id,
                state,
                actions_log,
            )
