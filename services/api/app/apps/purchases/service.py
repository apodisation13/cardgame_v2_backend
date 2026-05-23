import logging
import uuid

from lib.utils.db.pool import Database
from lib.utils.schemas.products import PurchaseStatus
from services.api.app.apps.purchases.schemas import Product, PurchaseProductResponse
from services.api.app.config import Config
from services.api.app.exceptions.exceptions import ProductDoesNotExistError, PurchaseDoesNotExistError


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

            # TODO: вот тут будет вызов скассы, которая вернет 2 параметра включая transaction_id
            transaction_id = str(uuid.uuid4())

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

        return PurchaseProductResponse(
            purchase_id=purchase_id,
            # confirmation_url=f"http://localhost:8080/payment/result?payment_id={purchase_id}",
            confirmation_url=None,
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
                    SELECT status FROM purchases WHERE user_id = $1 AND id = $2
                """,
                user_id,
                purchase_id,
            )

        if not status:
            raise PurchaseDoesNotExistError()

        return status
