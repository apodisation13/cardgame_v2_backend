from abc import ABC, abstractmethod
import asyncio
import logging

import httpx
from lib.utils.config.base import BaseConfig


logger = logging.getLogger(__name__)


class BaseClient(ABC):
    """Базовый класс для клиентов отправки сообщений"""

    def __init__(self, config: BaseConfig):
        self.config = config

    @abstractmethod
    async def send(self, to: str, message: str, subject: str | None = None) -> bool:
        """Отправка сообщения"""


class BaseHttpClient:
    """Базовый класс для HTTP-клиентов с ретраями"""

    def __init__(
        self,
        config: BaseConfig,
        base_url: str,
    ):
        self.config = config
        self.base_url = base_url

    def get_headers(self) -> dict:
        return {}

    async def request(
        self,
        method: str,
        path: str,
        *,
        retries: int = 3,
        timeout: int = 5,
        **kwargs,
    ) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            for attempt in range(retries):
                try:
                    response = await client.request(
                        method,
                        f"{self.base_url}{path}",
                        headers=self.get_headers(),
                        **kwargs,
                        timeout=timeout,
                    )
                    response.raise_for_status()
                    return response
                except httpx.HTTPStatusError as e:
                    if e.response.status_code < 500 or attempt == retries - 1:
                        logger.error("BaseHttpClient error: %s", e)
                        raise
                    logger.warning("BaseHttpClient retry number %s", attempt)
                    await asyncio.sleep(2**attempt)
                except httpx.RequestError as e:
                    if attempt == retries - 1:
                        logger.error("BaseHttpClient request failed: %s", e)
                        raise
                    logger.warning("BaseHttpClient retry number %s", attempt)
                    await asyncio.sleep(2**attempt)
