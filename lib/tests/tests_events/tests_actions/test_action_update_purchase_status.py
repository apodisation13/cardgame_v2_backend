import pytest

from lib.utils.events.action_types import ActionType
from lib.utils.events.actions.action_update_purchase_status import ActionUpdatePurchaseStatus
from lib.utils.events.event_types import EventType
from lib.utils.schemas.base import generate_uuid4_str
from lib.utils.schemas.events import ActionConfigData, ActionContext, AddResourcesSubtype
from lib.utils.schemas.game import ResourceType
from lib.utils.schemas.products import PaymentNotificationPaymentStatus, PurchaseStatus


@pytest.mark.asyncio
async def test_update_purchase_status_success_payment(
    # service fixtures
    config,
    db,
    db_connection,
    # fixtures for test
    user_factory,
    product_factory,
    purchase_factory,
    event_message_factory,
):
    user = await user_factory()

    product = await product_factory(
        data={
            "resources": {
                ResourceType.MONEY: 2000,
                ResourceType.WOOD: 1000,
                ResourceType.SCRAPS: 1500,
            },
        },
    )

    transaction_id = generate_uuid4_str()
    purchase = await purchase_factory(
        product_id=product.id,
        user_id=user.id,
        status=PurchaseStatus.PENDING,
        transaction_id=transaction_id,
    )

    event = event_message_factory(
        event_type=EventType.SUCCESS_PAYMENT,
        payload={
            "user_id": user.id,
            "purchase_id": purchase.id,
            "product_id": product.id,
            "subtype": AddResourcesSubtype.SUCCESS_PAYMENT,
            "state": PaymentNotificationPaymentStatus.PAYED,
        },
    )

    action_context = ActionContext(
        action_config=ActionConfigData(
            type=ActionType.UPDATE_PURCHASE_STATUS,
            conditions=True,
            receiver=None,
        ),
        payload=event.payload,
        event_type=event.event_type,
    )

    action = ActionUpdatePurchaseStatus(
        config=config,
        context=action_context,
        db=db,
    )

    await action.execute()

    purchases = await db_connection.fetch("""SELECT * FROM purchases""")
    assert len(purchases) == 1
    assert purchases[0]["id"] == purchase.id
    assert purchases[0]["user_id"] == user.id
    assert purchases[0]["status"] == PurchaseStatus.SUCCESS


@pytest.mark.asyncio
async def test_update_purchase_status_failed_payment(
    # service fixtures
    config,
    db,
    db_connection,
    # fixtures for test
    user_factory,
    product_factory,
    purchase_factory,
    event_message_factory,
):
    user = await user_factory()

    product = await product_factory(
        data={
            "resources": {
                ResourceType.MONEY: 2000,
                ResourceType.WOOD: 1000,
                ResourceType.SCRAPS: 1500,
            },
        },
    )

    transaction_id = generate_uuid4_str()
    purchase = await purchase_factory(
        product_id=product.id,
        user_id=user.id,
        status=PurchaseStatus.PENDING,
        transaction_id=transaction_id,
    )

    event = event_message_factory(
        event_type=EventType.FAILED_PAYMENT,
        payload={
            "user_id": user.id,
            "purchase_id": purchase.id,
            "product_id": product.id,
            "state": PaymentNotificationPaymentStatus.REJECTED,
        },
    )

    action_context = ActionContext(
        action_config=ActionConfigData(
            type=ActionType.UPDATE_PURCHASE_STATUS,
            conditions=True,
            receiver=None,
        ),
        payload=event.payload,
        event_type=event.event_type,
    )

    action = ActionUpdatePurchaseStatus(
        config=config,
        context=action_context,
        db=db,
    )

    await action.execute()

    purchases = await db_connection.fetch("""SELECT * FROM purchases""")
    assert len(purchases) == 1
    assert purchases[0]["id"] == purchase.id
    assert purchases[0]["user_id"] == user.id
    assert purchases[0]["status"] == PurchaseStatus.FAILED
