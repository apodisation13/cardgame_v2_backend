from lib.utils.clients.base import TelegramClient
from lib.utils.config.base import BaseConfig
from lib.utils.db.pool import Database
from lib.utils.events.actions.base import ActionBase
from lib.utils.events.uuu import render_template
from lib.utils.schemas.events import ActionConfigData


"""
    {
        "type": "ActionSendServiceTg",
        "message": "user {{ payload.user_id }} зарегистрирован",
        "conditions": true
    }
"""


class ActionSendServiceTg(ActionBase):
    def __init__(
        self,
        config: BaseConfig,
        action_config: ActionConfigData,
        payload: dict,
        db: Database = None,
    ) -> None:
        super().__init__(config=config, payload=payload, action_config=action_config, db=db)

        self.tg_client = TelegramClient(config)

    async def execute(self) -> None:
        if not self.action_config.message:
            return

        message = render_template(self.action_config.message, {"payload": self.payload})

        try:
            await self.tg_client.send(
                self.config.TG_CHAT_ID,
                message=message,
            )
        except Exception as e:
            raise RuntimeError(e) from e
