import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from lib.utils.events.action_types import ActionType
from lib.utils.events.event_types import EventProcessingActionStatus, EventProcessingState, EventType


def _make_action(
    condition=True,
    raise_on_execute=None,
) -> tuple:
    """Возвращает (action_class_mock, action_instance_mock)."""
    instance = MagicMock()
    instance.check_conditions.return_value = condition
    instance.execute = AsyncMock(side_effect=raise_on_execute)
    cls = MagicMock(return_value=instance)
    return cls, instance


def _processing(*action_types) -> list[dict]:
    return [{"type": at, "conditions": True} for at in action_types]


def _actions_log(row) -> dict:
    """actions_log хранится двойно-кодированным (процессор сам вызывает json.dumps,
    а коннекшн с JSONB-кодеком добавляет ещё один слой), поэтому декодируем вручную."""
    value = row["actions_log"]
    return json.loads(value) if isinstance(value, str) else value


@pytest.mark.asyncio
async def test_process_event_success(
    processor,
    db_connection,
    event_message_factory,
    event_config_factory,
    event_log_factory,
):
    """Все экшены выполнились без ошибок → SUCCESS."""
    event = event_message_factory(event_type=EventType.EVENT_1)
    await event_config_factory(
        type=EventType.EVENT_1,
        processing=_processing(ActionType.ADD_RESOURCES),
    )
    await event_log_factory(
        id=event.id,
        type=EventType.EVENT_1,
        state=EventProcessingState.SENT,
    )

    action_cls, _ = _make_action()

    with patch("lib.utils.events.event_processor.ACTION_REGISTRY", {ActionType.ADD_RESOURCES: action_cls}):
        await processor.process_event(event)

    row = await db_connection.fetchrow("SELECT * FROM event_log WHERE id = $1", event.id)
    assert row["state"] == EventProcessingState.SUCCESS
    assert row["type"] == EventType.EVENT_1
    assert row["retry_count"] == 0
    assert row["actions_log"] == [
        {
            'type': ActionType.ADD_RESOURCES,
            'state': EventProcessingActionStatus.SUCCESS,
        },
    ]


@pytest.mark.asyncio
async def test_process_event_action_raises_marks_failed(
    processor,
    db_connection,
    event_message_factory,
    event_config_factory,
    event_log_factory,
):
    """Экшен бросает исключение → FAILED."""
    event = event_message_factory(event_type=EventType.EVENT_1)
    await event_config_factory(
        type=EventType.EVENT_1,
        processing=_processing(ActionType.ADD_RESOURCES),
    )
    await event_log_factory(
        id=event.id,
        type=EventType.EVENT_1,
        state=EventProcessingState.SENT,
    )

    action_cls, _ = _make_action(raise_on_execute=ValueError("boom"))

    with patch("lib.utils.events.event_processor.ACTION_REGISTRY", {ActionType.ADD_RESOURCES: action_cls}):
        await processor.process_event(event)

    row = await db_connection.fetchrow("SELECT * FROM event_log WHERE id = $1", event.id)
    assert row["state"] == EventProcessingState.FAILED
    assert row["type"] == EventType.EVENT_1
    assert row["retry_count"] == 0
    assert row["actions_log"] == [
        {
            'type': ActionType.ADD_RESOURCES,
            'state': EventProcessingActionStatus.FAILED,
            "error": "boom",
        },
    ]


@pytest.mark.asyncio
async def test_process_event_partial_failure(
    processor,
    db_connection,
    event_message_factory,
    event_config_factory,
    event_log_factory,
):
    """Два экшена, второй падает → FAILED."""
    event = event_message_factory(event_type=EventType.EVENT_1)
    await event_config_factory(
        type=EventType.EVENT_1,
        processing=_processing(ActionType.ADD_RESOURCES, ActionType.SEND_SERVICE_TG),
    )
    await event_log_factory(
        id=event.id,
        type=EventType.EVENT_1,
        state=EventProcessingState.SENT,
    )

    action_ok_cls, _ = _make_action()
    action_fail_cls, _ = _make_action(raise_on_execute=RuntimeError("partial"))
    registry = {
        ActionType.ADD_RESOURCES: action_ok_cls,
        ActionType.SEND_SERVICE_TG: action_fail_cls,
    }

    with patch("lib.utils.events.event_processor.ACTION_REGISTRY", registry):
        await processor.process_event(event)

    row = await db_connection.fetchrow("SELECT * FROM event_log WHERE id = $1", event.id)
    print(row)
    assert row["state"] == EventProcessingState.FAILED
    states = {a["type"]: a["state"] for a in _actions_log(row)}
    assert states[ActionType.ADD_RESOURCES] == EventProcessingActionStatus.SUCCESS
    assert states[ActionType.SEND_SERVICE_TG] == EventProcessingActionStatus.FAILED


@pytest.mark.asyncio
async def test_process_event_config_not_found(
    processor,
    db_connection,
    event_message_factory,
    event_log_factory,
):
    """Нет конфига для типа события → FAILED, в лог пишется ошибка."""
    event = event_message_factory(event_type=EventType.EVENT_1)
    await event_log_factory(
        id=event.id,
        type=EventType.EVENT_1,
        state=EventProcessingState.SENT,
    )

    await processor.process_event(event)

    row = await db_connection.fetchrow("SELECT * FROM event_log WHERE id = $1", event.id)
    assert row["state"] == EventProcessingState.FAILED
    log = _actions_log(row)
    assert log[0]["type"] == "config"
    assert log[0]["state"] == EventProcessingActionStatus.FAILED


@pytest.mark.asyncio
async def test_process_event_unknown_action_type(
    processor,
    db_connection,
    event_message_factory,
    event_config_factory,
    event_log_factory,
):
    """Тип экшена отсутствует в реестре → ValueError → action FAILED."""
    event = event_message_factory(event_type=EventType.EVENT_1)
    await event_config_factory(
        type=EventType.EVENT_1,
        processing=_processing(ActionType.ADD_RESOURCES),
    )
    await event_log_factory(
        id=event.id,
        type=EventType.EVENT_1,
        state=EventProcessingState.SENT,
    )

    with patch("lib.utils.events.event_processor.ACTION_REGISTRY", {}):
        await processor.process_event(event)

    row = await db_connection.fetchrow("SELECT * FROM event_log WHERE id = $1", event.id)
    print(row)
    assert row["state"] == EventProcessingState.FAILED
    assert row["actions_log"] == [
        {
            'type': ActionType.ADD_RESOURCES,
            'error': 'Unknown action type: ActionAddResources',
            'state': EventProcessingActionStatus.FAILED,
        },
    ]


@pytest.mark.asyncio
async def test_process_event_condition_false_skips_execute(
    processor,
    db_connection,
    event_message_factory,
    event_config_factory,
    event_log_factory,
):
    """conditions=False → execute не вызывается, но результат считается SUCCESS."""
    event = event_message_factory(event_type=EventType.EVENT_1)
    await event_config_factory(
        type=EventType.EVENT_1,
        processing=_processing(ActionType.ADD_RESOURCES),
    )
    await event_log_factory(
        id=event.id,
        type=EventType.EVENT_1,
        state=EventProcessingState.SENT,
    )

    action_cls, action_instance = _make_action(condition=False)

    with patch("lib.utils.events.event_processor.ACTION_REGISTRY", {ActionType.ADD_RESOURCES: action_cls}):
        await processor.process_event(event)

    action_instance.execute.assert_not_called()

    row = await db_connection.fetchrow("SELECT * FROM event_log WHERE id = $1", event.id)
    assert row["state"] == EventProcessingState.SUCCESS
    assert row["actions_log"] == [
        {
            'type': ActionType.ADD_RESOURCES,
            'state': EventProcessingActionStatus.CONDITIONS_FALSE,
        },
    ]


@pytest.mark.asyncio
async def test_process_event_sets_in_progress_before_actions(
    processor,
    db_connection,
    event_message_factory,
    event_config_factory,
    event_log_factory,
):
    """IN_PROGRESS выставляется до запуска экшенов — проверяем из side_effect."""
    event = event_message_factory(event_type=EventType.EVENT_1)
    await event_config_factory(type=EventType.EVENT_1, processing=_processing(ActionType.ADD_RESOURCES))
    await event_log_factory(id=event.id, type=EventType.EVENT_1, state=EventProcessingState.SENT)

    state_during_action = []

    async def check_db_state():
        row = await db_connection.fetchrow("SELECT state FROM event_log WHERE id = $1", event.id)
        state_during_action.append(row["state"])

    action_cls, action_instance = _make_action()
    action_instance.execute.side_effect = check_db_state

    with patch("lib.utils.events.event_processor.ACTION_REGISTRY", {ActionType.ADD_RESOURCES: action_cls}):
        await processor.process_event(event)

    assert state_during_action[0] == EventProcessingState.IN_PROGRESS


@pytest.mark.asyncio
async def test_process_event_empty_processing_list(
    processor,
    db_connection,
    event_message_factory,
    event_config_factory,
    event_log_factory,
):
    """Пустой список экшенов → all([]) == True → SUCCESS."""
    event = event_message_factory(event_type=EventType.EVENT_1)
    await event_config_factory(type=EventType.EVENT_1, processing=[])
    await event_log_factory(id=event.id, type=EventType.EVENT_1, state=EventProcessingState.SENT)

    await processor.process_event(event)

    row = await db_connection.fetchrow("SELECT state FROM event_log WHERE id = $1", event.id)
    assert row["state"] == EventProcessingState.SUCCESS


@pytest.mark.asyncio
async def test_retry_success(
    processor,
    db_connection,
    event_message_factory,
    event_config_factory,
    event_log_factory,
):
    """Повтор упавшего экшена проходит → SUCCESS."""
    event = event_message_factory(event_type=EventType.EVENT_1)
    failed_log = [
        {
            "type": ActionType.ADD_RESOURCES,
            "state": EventProcessingActionStatus.FAILED,
            "error": "prev",
        },
    ]
    await event_config_factory(
        type=EventType.EVENT_1,
        processing=_processing(ActionType.ADD_RESOURCES),
    )
    await event_log_factory(
        id=event.id,
        type=EventType.EVENT_1,
        state=EventProcessingState.FAILED,
        actions_log=failed_log,
    )

    action_cls, _ = _make_action()

    with patch("lib.utils.events.event_processor.ACTION_REGISTRY", {ActionType.ADD_RESOURCES: action_cls}):
        await processor.retry_failed_actions(
            event_id=event.id,
            event_type=EventType.EVENT_1,
            payload=event.payload,
            actions_log=failed_log,
        )

    row = await db_connection.fetchrow("SELECT * FROM event_log WHERE id = $1", event.id)
    assert row["state"] == EventProcessingState.SUCCESS
    assert "error" not in _actions_log(row)[0]
    assert row["actions_log"] == [
        {
            'type': ActionType.ADD_RESOURCES,
            'state': EventProcessingActionStatus.SUCCESS,
        }
    ]


@pytest.mark.asyncio
async def test_retry_still_fails(
    processor,
    db_connection,
    event_message_factory,
    event_config_factory,
    event_log_factory,
):
    """Повтор снова падает → FAILED."""
    event = event_message_factory(event_type=EventType.EVENT_1)
    failed_log = [
        {
            "type": ActionType.ADD_RESOURCES,
            "state": EventProcessingActionStatus.FAILED,
            "error": "prev",
        },
    ]
    await event_config_factory(
        type=EventType.EVENT_1,
        processing=_processing(ActionType.ADD_RESOURCES),
    )
    await event_log_factory(
        id=event.id,
        type=EventType.EVENT_1,
        state=EventProcessingState.FAILED,
        actions_log=failed_log,
    )

    action_cls, _ = _make_action(raise_on_execute=RuntimeError("still broken"))

    with patch("lib.utils.events.event_processor.ACTION_REGISTRY", {ActionType.ADD_RESOURCES: action_cls}):
        await processor.retry_failed_actions(
            event_id=event.id,
            event_type=EventType.EVENT_1,
            payload=event.payload,
            actions_log=failed_log,
        )

    row = await db_connection.fetchrow("SELECT * FROM event_log WHERE id = $1", event.id)
    assert row["state"] == EventProcessingState.FAILED
    assert row["actions_log"][0]["type"] == ActionType.ADD_RESOURCES
    assert row["actions_log"][0]["state"] == EventProcessingActionStatus.FAILED


@pytest.mark.asyncio
async def test_retry_config_not_found_returns_early(
    processor,
    db_connection,
    event_message_factory,
    event_log_factory,
):
    """Конфиг не найден при ретрае → ранний выход, event_log не меняется."""
    event = event_message_factory(event_type=EventType.EVENT_1)
    original_log = [
        {
            "type": ActionType.ADD_RESOURCES,
            "state": EventProcessingActionStatus.FAILED,
            "error": "original",
        },
    ]
    await event_log_factory(
        id=event.id,
        type=EventType.EVENT_1,
        state=EventProcessingState.FAILED,
        actions_log=original_log,
    )

    await processor.retry_failed_actions(
        event_id=event.id,
        event_type=EventType.EVENT_1,
        payload=event.payload,
        actions_log=original_log,
    )

    row = await db_connection.fetchrow("SELECT state, actions_log FROM event_log WHERE id = $1", event.id)
    assert row["state"] == EventProcessingState.FAILED
    assert _actions_log(row)[0]["error"] == "original"


@pytest.mark.asyncio
async def test_retry_skips_successful_actions(
    processor,
    db_connection,
    event_message_factory,
    event_config_factory,
    event_log_factory,
):
    """Успешные экшены не ретраятся — только FAILED."""
    event = event_message_factory(event_type=EventType.EVENT_1)
    mixed_log = [
        {"type": ActionType.ADD_RESOURCES, "state": EventProcessingActionStatus.SUCCESS},
        {"type": ActionType.SEND_SERVICE_TG, "state": EventProcessingActionStatus.FAILED, "error": "prev"},
    ]
    await event_config_factory(
        type=EventType.EVENT_1,
        processing=_processing(ActionType.ADD_RESOURCES, ActionType.SEND_SERVICE_TG),
    )
    await event_log_factory(
        id=event.id,
        type=EventType.EVENT_1,
        state=EventProcessingState.FAILED,
        actions_log=mixed_log,
    )

    action_ok_cls, action_ok = _make_action()
    action_fixed_cls, action_fixed = _make_action()
    registry = {
        ActionType.ADD_RESOURCES: action_ok_cls,
        ActionType.SEND_SERVICE_TG: action_fixed_cls,
    }

    with patch("lib.utils.events.event_processor.ACTION_REGISTRY", registry):
        await processor.retry_failed_actions(
            event_id=event.id,
            event_type=EventType.EVENT_1,
            payload=event.payload,
            actions_log=mixed_log,
        )

    action_ok.execute.assert_not_called()
    action_fixed.execute.assert_called_once()

    row = await db_connection.fetchrow("SELECT * FROM event_log WHERE id = $1", event.id)
    assert row["state"] == EventProcessingState.SUCCESS
    assert row["actions_log"] == [
        {'type': ActionType.ADD_RESOURCES, 'state': EventProcessingActionStatus.SUCCESS},
        {'type': ActionType.SEND_SERVICE_TG, 'state': EventProcessingActionStatus.SUCCESS},
    ]


@pytest.mark.asyncio
async def test_retry_mixed_results(
    processor,
    db_connection,
    event_message_factory,
    event_config_factory,
    event_log_factory,
):
    """Один экшен исправился, другой нет → итог FAILED."""
    event = event_message_factory(event_type=EventType.EVENT_1)
    both_failed_log = [
        {"type": ActionType.ADD_RESOURCES, "state": EventProcessingActionStatus.FAILED, "error": "e1"},
        {"type": ActionType.SEND_SERVICE_TG, "state": EventProcessingActionStatus.FAILED, "error": "e2"},
    ]
    await event_config_factory(
        type=EventType.EVENT_1,
        processing=_processing(ActionType.ADD_RESOURCES, ActionType.SEND_SERVICE_TG),
    )
    await event_log_factory(
        id=event.id,
        type=EventType.EVENT_1,
        state=EventProcessingState.FAILED,
        actions_log=both_failed_log,
    )

    action_fixed_cls, _ = _make_action()
    action_broken_cls, _ = _make_action(raise_on_execute=RuntimeError("still broken"))
    registry = {
        ActionType.ADD_RESOURCES: action_fixed_cls,
        ActionType.SEND_SERVICE_TG: action_broken_cls,
    }

    with patch("lib.utils.events.event_processor.ACTION_REGISTRY", registry):
        await processor.retry_failed_actions(
            event_id=event.id,
            event_type=EventType.EVENT_1,
            payload=event.payload,
            actions_log=both_failed_log,
        )

    row = await db_connection.fetchrow("SELECT * FROM event_log WHERE id = $1", event.id)
    assert row["state"] == EventProcessingState.FAILED
    assert row["actions_log"][0]["type"] == ActionType.ADD_RESOURCES
    assert row["actions_log"][0]["state"] == EventProcessingActionStatus.SUCCESS
    assert row["actions_log"][1]["state"] == EventProcessingActionStatus.FAILED
    assert row["actions_log"][1]["type"] == ActionType.SEND_SERVICE_TG


@pytest.mark.asyncio
async def test_retry_conditions_false(
    processor,
    db_connection,
    event_message_factory,
    event_config_factory,
    event_log_factory,
):
    """При ретрае у экшена conditions=False → статус CONDITIONS_FALSE, событие SUCCESS."""
    event = event_message_factory(event_type=EventType.EVENT_1)
    failed_log = [
        {
            "type": ActionType.ADD_RESOURCES,
            "state": EventProcessingActionStatus.FAILED,
            "error": "prev",
        },
    ]
    await event_config_factory(
        type=EventType.EVENT_1,
        processing=_processing(ActionType.ADD_RESOURCES),
    )
    await event_log_factory(
        id=event.id,
        type=EventType.EVENT_1,
        state=EventProcessingState.FAILED,
        actions_log=failed_log,
    )

    action_cls, action_instance = _make_action(condition=False)

    with patch("lib.utils.events.event_processor.ACTION_REGISTRY", {ActionType.ADD_RESOURCES: action_cls}):
        await processor.retry_failed_actions(
            event_id=event.id,
            event_type=EventType.EVENT_1,
            payload=event.payload,
            actions_log=failed_log,
        )

    action_instance.execute.assert_not_called()
    row = await db_connection.fetchrow("SELECT * FROM event_log WHERE id = $1", event.id)
    assert row["state"] == EventProcessingState.SUCCESS
    assert _actions_log(row)[0]["state"] == EventProcessingActionStatus.CONDITIONS_FALSE
