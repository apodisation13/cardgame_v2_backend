from datetime import datetime, timedelta
import logging

from lib.utils.clients.ckassa import CKassaClient
from lib.utils.events import event_sender
from lib.utils.events.event_types import EventType
from lib.utils.schemas.events import AddResourcesSubtype
from lib.utils.schemas.products import PaymentNotificationPaymentStatus, PurchaseStatus
from lib.utils.tasks.base import TaskBase


logger = logging.getLogger(__name__)


class TaskCheckPendingPurchases(TaskBase):
    name = "task_check_pending_purchases"

    async def do(self) -> None:
        threshold = timedelta(minutes=self.config.PENDING_PURCHASES_THRESHOLD_MINUTES)

        async with self.db.connection() as connection:
            pending_purchases = await connection.fetch(
                """
                SELECT id, user_id, product_id, transaction_id
                FROM purchases
                WHERE status = $1
                AND created_at < $2
                """,
                PurchaseStatus.PENDING,
                datetime.now() - threshold,
            )

        if not pending_purchases:
            logger.info("No pending purchases to check")
            return

        logger.info("Found %d pending purchases to check", len(pending_purchases))

        ckassa_client = CKassaClient(self.config)
        ckassa_payments: list[dict] = await ckassa_client.get_payments()
        logger.info("Ckassa payments found: %s", ckassa_payments)

        ckassa_by_transaction_id = {t_id: p for p in ckassa_payments if (t_id := self._extract_transaction_id(p))}

        for purchase in pending_purchases:
            await self._process_purchase(
                purchase=purchase,
                ckassa_payment=ckassa_by_transaction_id.get(purchase["transaction_id"]),
            )

    def _extract_transaction_id(
        self,
        payment: dict,
    ) -> str | None:
        for prop in payment.get("properties", []):
            if prop.get("name") == "ФИО" or prop.get("name") == "НОМЕР ЗАКАЗА/СЧЕТА":
                return prop.get("value")
        return None

    async def _process_purchase(
        self,
        purchase: dict,
        ckassa_payment: dict | None,
    ) -> None:
        purchase_id = purchase["id"]
        transaction_id = purchase["transaction_id"]

        if ckassa_payment is None:
            logger.info("Purchase %s not found in CKassa, marking as abandoned", purchase_id)
            async with self.db.connection() as connection:
                await connection.execute(
                    """
                        UPDATE
                            purchases
                        SET
                            status = $1,
                            updated_at = NOW()
                        WHERE id = $2
                    """,
                    PurchaseStatus.ABANDONED,
                    purchase_id,
                )
            return

        state = ckassa_payment.get("state", "").lower()
        logger.info("Purchase %s found in CKassa with state %s", purchase_id, state)

        if state in PaymentNotificationPaymentStatus.success_states():
            await event_sender.create_event(
                event_type=EventType.SUCCESS_PAYMENT,
                payload={
                    "user_id": purchase["user_id"],
                    "purchase_id": purchase_id,
                    "product_id": purchase["product_id"],
                    "subtype": AddResourcesSubtype.SUCCESS_PAYMENT,
                    "state": state,
                    "transaction_id": transaction_id,
                },
                config=self.config,
                dedup_key=transaction_id,
            )
        elif state in PaymentNotificationPaymentStatus.failed_states():
            await event_sender.create_event(
                event_type=EventType.FAILED_PAYMENT,
                payload={
                    "user_id": purchase["user_id"],
                    "purchase_id": purchase_id,
                    "product_id": purchase["product_id"],
                    "state": state,
                    "transaction_id": transaction_id,
                },
                config=self.config,
                dedup_key=transaction_id,
            )
        else:
            logger.warning("Unknown CKassa state %s for purchase %s", state, purchase_id)
