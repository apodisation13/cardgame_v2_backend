import logging

from lib.utils.events.actions.base import ActionBase
from lib.utils.events.event_types import EventType
from lib.utils.schemas.products import PurchaseStatus


logger = logging.getLogger(__name__)


"""
    {
        "type": "ActionUpdatePurchaseStatus",
        "conditions": true
    }
    payload: { "user_id": int, "purchase_id": int }
"""


class ActionUpdatePurchaseStatus(ActionBase):
    async def execute(self) -> None:
        event_type: EventType = self.event_type

        event_status_map = {
            EventType.SUCCESS_PAYMENT: PurchaseStatus.SUCCESS,
            EventType.FAILED_PAYMENT: PurchaseStatus.FAILED,
        }

        status: PurchaseStatus | None = event_status_map.get(event_type)

        if not status:
            raise RuntimeError(f"Unknown event type: {event_type}")

        async with self.db.connection() as connection:
            await connection.execute(
                """
                UPDATE
                    purchases
                SET
                    status = $1,
                    updated_at = NOW()
                WHERE
                    purchases.id = $2
                    AND purchases.user_id = $3
                """,
                status,
                self.payload["purchase_id"],
                self.payload["user_id"],
            )
