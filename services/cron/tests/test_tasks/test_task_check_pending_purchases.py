from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest

from lib.utils.clients.ckassa import CKassaClient
from lib.utils.events.event_types import EventType
from lib.utils.schemas.products import PurchaseStatus
from services.cron.app.tasks.task_check_pending_purchases import TaskCheckPendingPurchases


def make_ckassa_payment(
    transaction_id: str,
    state: str,
) -> dict:
    return {
        "properties": [{"name": "ФИО", "value": transaction_id}],
        "state": state,
        "amount": 10000,
    }


OLD_CREATED_AT = datetime.now(tz=UTC) - timedelta(hours=1)
RECENT_CREATED_AT = datetime.now(tz=UTC) - timedelta(minutes=5)


@pytest.mark.asyncio
async def test_success_payment_creates_event(
    config,
    db,
    db_connection,
    user_factory,
    product_factory,
    purchase_factory,
    event_sender_mock,
):
    user = await user_factory()
    product = await product_factory()
    await purchase_factory(
        user_id=user.id,
        product_id=product.id,
        transaction_id="tx-success-1",
        created_at=OLD_CREATED_AT,
    )

    ckassa_response = [make_ckassa_payment("tx-success-1", "payed")]

    with patch.object(CKassaClient, "get_payments", new_callable=AsyncMock, return_value=ckassa_response):
        task = TaskCheckPendingPurchases(config, db)
        await task.do()

    event_sender_mock.assert_awaited_once()
    call_kwargs = event_sender_mock.call_args.kwargs
    assert call_kwargs["event_type"] == EventType.SUCCESS_PAYMENT
    assert call_kwargs["dedup_key"] == "tx-success-1"


@pytest.mark.asyncio
async def test_failed_payment_creates_event(
    config,
    db,
    db_connection,
    user_factory,
    product_factory,
    purchase_factory,
    event_sender_mock,
):
    user = await user_factory()
    product = await product_factory()
    await purchase_factory(
        user_id=user.id,
        product_id=product.id,
        transaction_id="tx-failed-1",
        created_at=OLD_CREATED_AT,
    )

    ckassa_response = [make_ckassa_payment("tx-failed-1", "rejected")]

    with patch.object(CKassaClient, "get_payments", new_callable=AsyncMock, return_value=ckassa_response):
        task = TaskCheckPendingPurchases(config, db)
        await task.do()

    event_sender_mock.assert_awaited_once()
    call_kwargs = event_sender_mock.call_args.kwargs
    assert call_kwargs["event_type"] == EventType.FAILED_PAYMENT
    assert call_kwargs["dedup_key"] == "tx-failed-1"


@pytest.mark.asyncio
async def test_not_found_in_ckassa_marks_abandoned(
    config,
    db,
    db_connection,
    user_factory,
    product_factory,
    purchase_factory,
    event_sender_mock,
):
    user = await user_factory()
    product = await product_factory()
    purchase = await purchase_factory(
        user_id=user.id,
        product_id=product.id,
        transaction_id="tx-abandoned-1",
        created_at=OLD_CREATED_AT,
    )

    with patch.object(CKassaClient, "get_payments", new_callable=AsyncMock, return_value=[]):
        task = TaskCheckPendingPurchases(config, db)
        await task.do()

    event_sender_mock.assert_not_awaited()

    status = await db_connection.fetchval("SELECT status FROM purchases WHERE id = $1", purchase.id)
    assert status == PurchaseStatus.ABANDONED


@pytest.mark.asyncio
async def test_recent_purchases_are_skipped(
    config,
    db,
    db_connection,
    user_factory,
    product_factory,
    purchase_factory,
    event_sender_mock,
):
    user = await user_factory()
    product = await product_factory()
    await purchase_factory(
        user_id=user.id,
        product_id=product.id,
        transaction_id="tx-recent-1",
        created_at=RECENT_CREATED_AT,
    )

    with patch.object(CKassaClient, "get_payments", new_callable=AsyncMock, return_value=[]):
        task = TaskCheckPendingPurchases(config, db)
        await task.do()

    event_sender_mock.assert_not_awaited()

    status = await db_connection.fetchval("SELECT status FROM purchases WHERE transaction_id = $1", "tx-recent-1")
    assert status == PurchaseStatus.PENDING


@pytest.mark.asyncio
async def test_mixed_batch(
    config,
    db,
    db_connection,
    user_factory,
    product_factory,
    purchase_factory,
    event_sender_mock,
):
    user = await user_factory()
    product = await product_factory()

    await purchase_factory(
        user_id=user.id,
        product_id=product.id,
        transaction_id="tx-mix-1",
        created_at=OLD_CREATED_AT,
    )
    await purchase_factory(
        user_id=user.id,
        product_id=product.id,
        transaction_id="tx-mix-2",
        created_at=OLD_CREATED_AT,
    )
    p_abandoned = await purchase_factory(
        user_id=user.id,
        product_id=product.id,
        transaction_id="tx-mix-3",
        created_at=OLD_CREATED_AT,
    )

    ckassa_response = [
        make_ckassa_payment("tx-mix-1", "payed"),
        make_ckassa_payment("tx-mix-2", "rejected"),
    ]

    with patch.object(CKassaClient, "get_payments", new_callable=AsyncMock, return_value=ckassa_response):
        task = TaskCheckPendingPurchases(config, db)
        await task.do()

    assert event_sender_mock.await_count == 2

    event_types = {call.kwargs["event_type"] for call in event_sender_mock.call_args_list}
    assert EventType.SUCCESS_PAYMENT in event_types
    assert EventType.FAILED_PAYMENT in event_types

    abandoned_status = await db_connection.fetchval(
        "SELECT status FROM purchases WHERE id = $1",
        p_abandoned.id,
    )
    assert abandoned_status == PurchaseStatus.ABANDONED
