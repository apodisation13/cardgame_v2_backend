import pytest

from lib.utils.events.action_types import ActionType
from lib.utils.events.actions.action_add_resources import ActionAddResources
from lib.utils.schemas.events import ActionConfigData


@pytest.mark.asyncio
async def test_add_resources_credits_user(
    # service fixtures
    config,
    db,
    db_connection,
    # fixtures for test
    user_factory,
    user_resource_factory,
    event_message_factory,
):
    user = await user_factory()
    await user_resource_factory(id=user.id, wood=1000, money=2000)

    event = event_message_factory(
        event_type="event_1",
        payload={"user_id": user.id, "wood": 100, "money": 500},
    )

    action = ActionAddResources(
        config=config,
        action_config=ActionConfigData(
            type=ActionType.ADD_RESOURCES,
            conditions=True,
            receiver=None,
        ),
        payload=event.payload,
        db=db,
    )

    await action.execute()

    row = await db_connection.fetchrow(
        "SELECT wood, money FROM user_resources WHERE id = $1",
        user.id,
    )
    assert row["wood"] == 1100
    assert row["money"] == 2500


@pytest.mark.asyncio
async def test_add_resources_partial_fields(
    config,
    db,
    db_connection,
    user_factory,
    user_resource_factory,
    event_message_factory,
):
    """Только часть ресурсов в payload — остальные не должны измениться."""
    user = await user_factory()
    await user_resource_factory(id=user.id, scraps=500, wood=1000, money=2000)

    event = event_message_factory(
        payload={"user_id": user.id, "scraps": 200},
    )

    action = ActionAddResources(
        config=config,
        action_config=ActionConfigData(
            type=ActionType.ADD_RESOURCES,
            conditions=True,
            receiver=None,
        ),
        payload=event.payload,
        db=db,
    )

    await action.execute()

    row = await db_connection.fetchrow(
        "SELECT scraps, wood, money FROM user_resources WHERE id = $1",
        user.id,
    )
    assert row["scraps"] == 700
    assert row["wood"] == 1000  # не изменился
    assert row["money"] == 2000  # не изменился


@pytest.mark.asyncio
async def test_add_resources_skips_unknown_fields(
    config,
    db,
    db_connection,
    user_factory,
    user_resource_factory,
    event_message_factory,
):
    """Неизвестные поля в payload игнорируются, ресурсы не меняются."""
    user = await user_factory()
    await user_resource_factory(id=user.id, money=2000)

    event = event_message_factory(
        payload={"user_id": user.id, "unknown_field": 999},
    )

    action = ActionAddResources(
        config=config,
        action_config=ActionConfigData(
            type=ActionType.ADD_RESOURCES,
            conditions=True,
            receiver=None,
        ),
        payload=event.payload,
        db=db,
    )

    await action.execute()

    row = await db_connection.fetchrow(
        "SELECT money FROM user_resources WHERE id = $1",
        user.id,
    )
    assert row["money"] == 2000
