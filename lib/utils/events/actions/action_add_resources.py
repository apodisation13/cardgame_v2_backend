import logging

from lib.utils.events.actions.base import ActionBase
from lib.utils.schemas.events import AddResourcesSubtype
from lib.utils.schemas.game import ResourceType
from lib.utils.schemas.products import PurchaseStatus


logger = logging.getLogger(__name__)

_RESOURCE_FIELDS = frozenset(ResourceType)


"""
    {
        "type": "ActionAddResources",
        "conditions": true
    }
    payload: { "user_id": int, "subtype": "direct", "resources": { "money": 2000, "scraps": 1000 } },
    payload: { "user_id": int, "subtype": "success_payment", "product_id": int, "purchase_id": int  },
"""


class ActionAddResources(ActionBase):
    async def execute(self) -> None:
        user_id = self.payload["user_id"]

        subtype: AddResourcesSubtype = self.payload["subtype"]

        logger.info("Adding resources for user %s, subtype %s", user_id, subtype)

        if subtype not in AddResourcesSubtype.processable_subtypes():
            raise RuntimeError(f"Invalid subtype {subtype}")

        if subtype == AddResourcesSubtype.DIRECT:
            resources = {k: v for k, v in self.payload["resources"].items() if k in _RESOURCE_FIELDS}

        elif subtype == AddResourcesSubtype.SUCCESS_PAYMENT:
            product_id = self.payload["product_id"]
            purchase_id = self.payload["purchase_id"]

            logger.info(
                "Adding resources for user %s, product %s, purchase %s",
                user_id,
                product_id,
                purchase_id,
            )

            async with self.db.connection() as connection:
                purchased_product_resources: dict | None = await connection.fetchval(
                    """
                    SELECT
                        products.data -> 'resources' AS resources_to_pay
                    FROM
                        purchases
                    JOIN
                        products ON purchases.product_id = products.id
                    WHERE
                        purchases.id = $1
                        AND purchases.product_id = $2
                        AND purchases.user_id = $3
                        AND purchases.status = $4
                    """,
                    purchase_id,
                    product_id,
                    user_id,
                    PurchaseStatus.SUCCESS,
                )

                if not purchased_product_resources:
                    logger.error("User %s has no resources for product %s", user_id, product_id)
                    raise RuntimeError(f"Purchase {purchase_id} has no resources")

                resources = {k: v for k, v in purchased_product_resources.items() if k in _RESOURCE_FIELDS}

        if not resources:
            logger.warning("No resources to add for user %s, payload %s", user_id, self.payload)
            return

        set_clauses = ", ".join(f"{col} = {col} + ${i + 2}" for i, col in enumerate(resources))

        async with self.db.connection() as connection:
            await connection.execute(
                f"UPDATE user_resources SET {set_clauses} WHERE id = $1",  # noqa: S608
                user_id,
                *resources.values(),
            )
