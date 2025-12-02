from lib.utils.clients.base import EmailClient, SmsClient, TelegramClient
from lib.utils.config.base import BaseConfig
from lib.utils.events.actions.base import ActionBase
from lib.utils.events.uuu import render_template
from lib.utils.schemas.events import ActionConfigData


class SendSmsAction(ActionBase):
    def __init__(
        self,
        config: BaseConfig,
        action_config: ActionConfigData,
        payload: dict,
    ) -> None:
        super().__init__(
            config=config,
            payload=payload,
            action_config=action_config,
        )

        self.email_client = EmailClient(config)
        self.sms_client = SmsClient(config)
        self.tg_client = TelegramClient(config)

    async def execute(
        self,
        payload: dict,
    ) -> None:
        print("STR19", type(payload), payload)

        receiver_template = self.action_config.receiver
        print("STR35", receiver_template)
        receiver = render_template(receiver_template, payload)
        print("STR37", receiver)

        try:
            # await self.email_client.send(receiver, "HELLO!!!!", subject="hi")
            await self.tg_client.send(self.config.TG_CHAT_ID, message="hello from app")
            # await self.sms_client.send("79104959509", message="hello-sms from app")

            print(f"Sending SMS to {receiver}")
        except Exception as e:
            raise RuntimeError(e) from e
