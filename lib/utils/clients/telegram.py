import logging

from lib.utils.clients.base import BaseClient, BaseHttpClient
from lib.utils.config.base import BaseConfig


logger = logging.getLogger(__name__)


class TelegramClient(BaseClient, BaseHttpClient):
    """Клиент для отправки сообщений в Telegram"""

    def __init__(
        self,
        config: BaseConfig,
    ):
        BaseClient.__init__(self, config)
        BaseHttpClient.__init__(self, base_url=config.TG_BASE_URL, config=config)

    def get_headers(self) -> dict:
        return {"X-Secret": self.config.TG_PROXY_SECRET}

    async def send(
        self,
        to: str,
        message: str,
        subject: str | None = None,
    ) -> None:
        payload = {
            "chat_id": to,
            "text": message,
            "parse_mode": "HTML",
        }
        try:
            response = await self.request(
                "POST",
                f"/bot{self.config.TG_TOKEN}/sendMessage",
                data=payload,
                timeout=30,
            )
            result = response.json()
            if result.get("ok"):
                logger.info("Сообщение отправлено в Telegram chat_id: %s", to)
            else:
                logger.error("Ошибка Telegram API: %s", result.get("description"))
        except Exception as e:
            logger.error("Ошибка отправки в Telegram: %s", e)
            raise RuntimeError from e
