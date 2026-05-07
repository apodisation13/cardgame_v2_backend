import logging

from lib.utils.db.pool import Database
from services.api.app.apps.purchases.schemas import Product
from services.api.app.config import Config

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
                """
            )

        return [Product.get_one(row) for row in rows]
