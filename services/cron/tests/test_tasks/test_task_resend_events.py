import pytest

from lib.utils.events.action_types import ActionType
from lib.utils.events.event_types import EventProcessingActionStatus, EventProcessingState, EventType
from services.cron.app.tasks import TaskResendEvents


@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_database")
async def test_task_resend_events(
    config,
    db,
    db_connection,
    # fixtures for test
    event_log_factory,
    event_message_factory,
    event_config_factory,
):
    event = event_message_factory(event_type=EventType.EVENT_1)
    await event_config_factory(
        type=EventType.EVENT_1,
        processing=[
            {"type": ActionType.ADD_RESOURCES, "conditions": True},
            {"type": ActionType.SEND_SERVICE_TG, "conditions": True},
        ],
    )

    mixed_log = [
        {"type": ActionType.ADD_RESOURCES, "state": EventProcessingActionStatus.SUCCESS},
        {"type": ActionType.SEND_SERVICE_TG, "state": EventProcessingActionStatus.FAILED, "error": "prev"},
    ]
    await event_log_factory(
        id=event.id,
        type=EventType.EVENT_1,
        state=EventProcessingState.FAILED,
        actions_log=mixed_log,
    )

    # а этот не пойдет, у него retry_count = 3
    await event_log_factory(
        type=EventType.EVENT_1,
        state=EventProcessingState.FAILED,
        actions_log=mixed_log,
        retry_count=3,
    )
    # и этот не пойдет, он успешный
    await event_log_factory(
        type=EventType.EVENT_1,
        state=EventProcessingState.SUCCESS,
        actions_log=mixed_log,
        retry_count=3,
    )

    task = TaskResendEvents(config, db)

    # Запускаем задачу
    await task.do()

    result_event_log = await db_connection.fetch("SELECT * FROM event_log ORDER BY updated_at DESC")
    assert len(result_event_log) == 3

    assert result_event_log[0]["id"] == event.id
    assert result_event_log[0]["type"] == EventType.EVENT_1
    assert result_event_log[0]["state"] == EventProcessingState.SUCCESS
    assert result_event_log[0]["actions_log"] == [
        {"type": ActionType.ADD_RESOURCES, "state": EventProcessingActionStatus.SUCCESS},
        {"type": ActionType.SEND_SERVICE_TG, "state": EventProcessingActionStatus.SUCCESS},
    ]
    assert result_event_log[0]["retry_count"] == 1
