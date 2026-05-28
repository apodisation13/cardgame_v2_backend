import logging

from lib.utils.clients.ckassa import CKassaClient
from lib.utils.config.env_types import EnvType
from lib.utils.db.pool import Database
from lib.utils.events import event_sender
from lib.utils.events.event_types import EventType
from lib.utils.schemas.base import generate_uuid4_str
from lib.utils.schemas.events import AddResourcesSubtype
from lib.utils.schemas.products import PaymentNotificationPaymentStatus, PurchaseStatus
from services.api.app.apps.purchases.schemas import Product, PurchaseProductResponse
from services.api.app.config import Config
from services.api.app.exceptions.exceptions import (
    PaymentNotificationProcessError,
    ProductDoesNotExistError,
    PurchaseDoesNotExistError,
)


logger = logging.getLogger(__name__)


class PurchasesService:
    def __init__(
        self,
        db_pool: Database,
        config: Config,
    ):
        self.db_pool = db_pool
        self.config = config

    async def get_all_products(self) -> list[Product]:
        async with self.db_pool.connection() as connection:
            rows = await connection.fetch(
                """
                    SELECT
                        id,
                        title,
                        data,
                        price,
                        type
                    FROM
                        products
                    WHERE
                        is_active is TRUE
                    ORDER BY
                        priority DESC,
                        price,
                        updated_at DESC
                """,
            )

        return [Product.get_one(row) for row in rows]

    async def purchase_product(
        self,
        ckassa_client: CKassaClient,
        user_id: int,
        product_id: int,
    ) -> PurchaseProductResponse:
        logger.info("User %s is about to purchase product %s", user_id, product_id)
        async with self.db_pool.connection() as connection:
            product_info: dict = await connection.fetchrow(
                """
                SELECT
                    products.price,
                    products.title
                FROM
                    products
                WHERE
                    is_active IS TRUE
                    AND products.id = $1
                """,
                product_id,
            )

            logger.info("Product info %s", product_info)

            if not product_info:
                raise ProductDoesNotExistError()

            transaction_id = generate_uuid4_str()

            # костыль для локального запуска: в тесте у них можно передать только небольшое значение
            if self.config.ENV_TYPE == EnvType.DEVELOPMENT_LOCAL:
                transaction_id = transaction_id[:15]

            purchase_id: int = await connection.fetchval(
                """
                INSERT INTO purchases
                (user_id, product_id, amount, transaction_id)
                VALUES ($1, $2, $3, $4)
                RETURNING id
                """,
                user_id,
                product_id,
                product_info["price"],
                transaction_id,
            )
            logger.info("Purchase created, %s", purchase_id)

            payment_url: str = await ckassa_client.create_invoice(
                amount_rub=product_info["price"],
                transaction_id=transaction_id,
            )
            logger.info("Payment url %s for transaction %s", payment_url, transaction_id)

        return PurchaseProductResponse(
            purchase_id=purchase_id,
            payment_url=payment_url,
            transaction_id=transaction_id,
        )

    async def get_purchase_status(
        self,
        user_id: int,
        purchase_id: int,
    ) -> PurchaseStatus:
        logger.info("Polling purchase %s for user %s", purchase_id, user_id)

        async with self.db_pool.connection() as connection:
            status: PurchaseStatus | None = await connection.fetchval(
                """
                    SELECT
                        status
                    FROM
                        purchases
                    WHERE
                        purchases.id = $1
                        AND purchases.user_id = $2
                """,
                purchase_id,
                user_id,
            )
            logger.info("Purchase: %s, status: %s", purchase_id, status)

        if not status:
            raise PurchaseDoesNotExistError()

        return status

    async def process_payment_notification(
        self,
        data: dict,
    ) -> None:
        logger.info("Processing payment notification: %s", data)

        # Да, вот именно так и будет лежать уникальное поле - в графе ФИО
        # техническая особенность платежной системы
        transaction_id: str | None = data.get("property", {}).get("ФИО")

        if not transaction_id:
            msg = "No transaction provided for payment notification: %s"
            logger.error(msg, data)
            raise PaymentNotificationProcessError(msg % data)

        state: PaymentNotificationPaymentStatus | str = data.get("state", "").lower()

        if not state:
            msg = "No status provided for payment notification: %s"
            logger.error(msg, data)
            raise PaymentNotificationProcessError(msg % data)

        if state not in PaymentNotificationPaymentStatus.processable_states():
            msg = "Unknown state for payment notification: %s"
            logger.error(msg, state)
            raise PaymentNotificationProcessError(msg % state)

        async with self.db_pool.connection() as connection:
            purchase: dict | None = await connection.fetchrow(
                """
                SELECT
                    purchases.id,
                    purchases.user_id,
                    purchases.product_id
                FROM
                    purchases
                WHERE
                    transaction_id = $1
                    AND purchases.status = $2
                """,
                transaction_id,
                PurchaseStatus.PENDING,
            )

        if not purchase:
            msg = "No purchase such purchase (transaction) found: %s"
            logger.error(msg, transaction_id)
            raise PaymentNotificationProcessError(msg % transaction_id)

        if state in PaymentNotificationPaymentStatus.success_states():
            await event_sender.create_event(
                event_type=EventType.SUCCESS_PAYMENT,
                payload={
                    "user_id": purchase["user_id"],
                    "purchase_id": purchase["id"],
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
                    "purchase_id": purchase["id"],
                    "product_id": purchase["product_id"],
                    "state": state,
                    "transaction_id": transaction_id,
                },
                config=self.config,
                dedup_key=transaction_id,
            )

        else:
            logger.error("Unknown state for payment notification: %s", state)
