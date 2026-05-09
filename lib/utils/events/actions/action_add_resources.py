from lib.utils.config.base import BaseConfig
from lib.utils.db.pool import Database
from lib.utils.events.actions.base import ActionBase
from lib.utils.schemas.events import ActionConfigData
from lib.utils.schemas.game import ResourceType


_RESOURCE_FIELDS = frozenset(ResourceType)


class ActionAddResources(ActionBase):
    def __init__(
        self,
        config: BaseConfig,
        action_config: ActionConfigData,
        payload: dict,
        db: Database,
    ) -> None:
        super().__init__(config=config, payload=payload, action_config=action_config, db=db)

    async def execute(self) -> None:
        user_id = self.payload["user_id"]
        resources = {k: v for k, v in self.payload.items() if k in _RESOURCE_FIELDS}

        if not resources:
            return

        set_clauses = ", ".join(
            f"{col} = {col} + ${i + 2}"
            for i, col in enumerate(resources)
        )

        async with self.db.connection() as conn:
            await conn.execute(
                f"UPDATE user_resources SET {set_clauses} WHERE id = $1",  # noqa: S608
                user_id,
                *resources.values(),
            )