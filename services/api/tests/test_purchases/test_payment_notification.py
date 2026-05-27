import pytest

from httpx import AsyncClient
from lib.utils.events.event_types import EventType
from lib.utils.schemas.base import generate_uuid4_str
from lib.utils.schemas.game import ResourceType
from lib.utils.schemas.products import PaymentNotificationPaymentStatus, PurchaseStatus


class TestPaymentNotificationAPI:
    endpoint = "/payment-notification"

    @pytest.mark.usefixtures("event_processor_fixture")
    @pytest.mark.asyncio
    async def test_payment_notification_success_payment(
        self,
        # service fixtures
        client: AsyncClient,
        db_connection,
        user_login_fixture,
        # fixtures for test
        user_resource_factory,
        product_factory,
        purchase_factory,
        event_message_factory,
        event_config_factory,
    ):
        user_id = user_login_fixture["id"]
        await user_resource_factory(
            id=user_id,
            money=3000,
            wood=1000,
            scraps=2000,
        )

        event_message_factory(
            event_type=EventType.SUCCESS_PAYMENT,
        )
        await event_config_factory(
            type=EventType.SUCCESS_PAYMENT,
            processing=[
                {
                    "type": "ActionUpdatePurchaseStatus",
                    "conditions": True,
                },
                {
                    "type": "ActionAddResources",
                    "conditions": True,
                },
            ],
        )

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
            user_id=user_id,
            status=PurchaseStatus.PENDING,
            transaction_id=transaction_id,
        )

        response = await client.post(
            self.endpoint,
            json={
                "regPayNum": "1310958041",
                "property": {
                    "ФИО": transaction_id,
                },
                "rrn": "315659894693",
                "irn": "f631e778-fs4d-dc19-sdc6-251e02666345",
                "approvalCode": "123456789",
                "cardPan": "411111*****1111",
                "amount": "100000",
                "state": PaymentNotificationPaymentStatus.PAYED,
                "result": {
                    "code": "0",
                    "message": "null",
                    "details": "null",
                },
                "created": "20-06-2023 17:56:36",
            },
        )

        assert response.status_code == 200

        purchases_result = await db_connection.fetch("""SELECT * FROM purchases""")
        assert len(purchases_result) == 1

        assert purchases_result[0]["id"] == purchase.id
        assert purchases_result[0]["transaction_id"] == transaction_id
        assert purchases_result[0]["status"] == PurchaseStatus.SUCCESS

        user_resources = await db_connection.fetch("""SELECT * FROM user_resources""")
        assert len(user_resources) == 1
        assert user_resources[0]["id"] == user_id
        assert user_resources[0]["money"] == 3000 + 2000
        assert user_resources[0]["wood"] == 1000 + 1000
        assert user_resources[0]["scraps"] == 2000 + 1500

        # Тот же самый запрос второй раз уже не пройдет - потому что статус покупки УЖЕ обновлен
        response = await client.post(
            self.endpoint,
            json={
                "regPayNum": "1310958041",
                "property": {
                    "ФИО": transaction_id,
                },
                "rrn": "315659894693",
                "irn": "f631e778-fs4d-dc19-sdc6-251e02666345",
                "approvalCode": "123456789",
                "cardPan": "411111*****1111",
                "amount": "100000",
                "state": PaymentNotificationPaymentStatus.PAYED,
                "result": {
                    "code": "0",
                    "message": "null",
                    "details": "null",
                },
                "created": "20-06-2023 17:56:36",
            },
        )

        assert response.status_code == 400

        msg = f"No purchase such purchase (transaction) found: {transaction_id}"
        assert response.json() == {
            "error": {
                "code": "BAD_REQUEST",
                "message": msg,
                "details": f"PaymentNotificationProcessError('{msg}')",
            },
        }

    @pytest.mark.usefixtures("event_processor_fixture")
    @pytest.mark.asyncio
    async def test_payment_notification_failed_payment(
        self,
        # service fixtures
        client: AsyncClient,
        db_connection,
        user_login_fixture,
        # fixtures for test
        user_resource_factory,
        product_factory,
        purchase_factory,
        event_message_factory,
        event_config_factory,
    ):
        user_id = user_login_fixture["id"]
        await user_resource_factory(
            id=user_id,
            money=3000,
            wood=1000,
            scraps=2000,
        )

        event_message_factory(
            event_type=EventType.FAILED_PAYMENT,
        )
        await event_config_factory(
            type=EventType.FAILED_PAYMENT,
            processing=[
                {
                    "type": "ActionUpdatePurchaseStatus",
                    "conditions": True,
                },
            ],
        )

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
            user_id=user_id,
            status=PurchaseStatus.PENDING,
            transaction_id=transaction_id,
        )

        response = await client.post(
            self.endpoint,
            json={
                "regPayNum": "1310958041",
                "property": {
                    "ФИО": transaction_id,
                },
                "rrn": "315659894693",
                "irn": "f631e778-fs4d-dc19-sdc6-251e02666345",
                "approvalCode": "123456789",
                "cardPan": "411111*****1111",
                "amount": "100000",
                "state": PaymentNotificationPaymentStatus.REJECTED,
                "result": {
                    "code": "0",
                    "message": "null",
                    "details": "null",
                },
                "created": "20-06-2023 17:56:36",
            },
        )

        assert response.status_code == 200

        purchases_result = await db_connection.fetch("""SELECT * FROM purchases""")
        assert len(purchases_result) == 1

        assert purchases_result[0]["id"] == purchase.id
        assert purchases_result[0]["transaction_id"] == transaction_id
        assert purchases_result[0]["status"] == PurchaseStatus.FAILED

        user_resources = await db_connection.fetch("""SELECT * FROM user_resources""")
        assert len(user_resources) == 1
        assert user_resources[0]["id"] == user_id
        assert user_resources[0]["money"] == 3000
        assert user_resources[0]["wood"] == 1000
        assert user_resources[0]["scraps"] == 2000

    @pytest.mark.asyncio
    async def test_payment_notification_without_transaction_or_state(
        self,
        # service fixtures
        client: AsyncClient,
    ):
        payload = {
            "regPayNum": "1310958041",
            "property": {
                "smth_else": "i-dont-know-what",
            },
        }
        response = await client.post(
            self.endpoint,
            json=payload,
        )

        assert response.status_code == 400

        error_msg = f"No transaction provided for payment notification: {payload}"
        assert response.json() == {
            "error": {
                "code": "BAD_REQUEST",
                "message": error_msg,
                "details": f'PaymentNotificationProcessError("{error_msg}")',
            },
        }

        # 2й кейс - нет статуса
        payload = {
            "regPayNum": "1310958041",
            "property": {
                "ФИО": "transaction_id",
            },
        }
        response = await client.post(
            self.endpoint,
            json=payload,
        )

        assert response.status_code == 400

        error_msg = f"No status provided for payment notification: {payload}"
        assert response.json() == {
            "error": {
                "code": "BAD_REQUEST",
                "message": error_msg,
                "details": f'PaymentNotificationProcessError("{error_msg}")',
            },
        }

    @pytest.mark.asyncio
    async def test_payment_notification_wrong_state(
        self,
        # service fixtures
        client: AsyncClient,
    ):
        payload = {
            "regPayNum": "1310958041",
            "state": "SOME_WRONG_STATE",
            "property": {
                "ФИО": "transaction_id",
            },
        }
        response = await client.post(
            self.endpoint,
            json=payload,
        )

        assert response.status_code == 400

        error_msg = "Unknown state for payment notification: SOME_WRONG_STATE"
        assert response.json() == {
            "error": {
                "code": "BAD_REQUEST",
                "message": error_msg,
                "details": f"PaymentNotificationProcessError('{error_msg}')",
            },
        }

    @pytest.mark.asyncio
    async def test_payment_notification_no_such_purchase(
        self,
        # service fixtures
        client: AsyncClient,
    ):
        payload = {
            "regPayNum": "1310958041",
            "state": PaymentNotificationPaymentStatus.REJECTED,
            "property": {
                "ФИО": "transaction_id",
            },
        }
        response = await client.post(
            self.endpoint,
            json=payload,
        )

        assert response.status_code == 400

        error_msg = "No purchase such purchase (transaction) found: transaction_id"
        assert response.json() == {
            "error": {
                "code": "BAD_REQUEST",
                "message": error_msg,
                "details": f"PaymentNotificationProcessError('{error_msg}')",
            },
        }
