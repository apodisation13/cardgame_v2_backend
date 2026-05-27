from datetime import datetime, timezone, timedelta

from lib.utils.clients import BaseHttpClient
from lib.utils.config.base import BaseConfig


class CKassaClient(BaseHttpClient):
    def __init__(
        self,
        config: BaseConfig,
    ):
        super().__init__(config=config, base_url=config.CKASSA_BASE_URL)

    def get_headers(self) -> dict:
        print(self.config.CKASSA_SERV_CODE, self.config.CKASSA_API_LOGIN, self.config.CKASSA_BASE_URL)
        return {
            "ApiLoginAuthorization": self.config.CKASSA_API_LOGIN,
            "ApiAuthorization": self.config.CKASSA_API_SECRET_KEY,
        }

    async def create_invoice(
        self,
        amount_rub: float,
        transaction_id: str,
    ) -> str:
        deadline = datetime.now(tz=timezone.utc) + timedelta(minutes=self.config.CKASSA_PAYMENT_TIMEOUT_MINUTES)
        deadline.strftime("%d-%m-%Y %H:%M:%S +0000")

        payload = {
            "servCode": self.config.CKASSA_SERV_CODE,
            "tgInvPayer": "string",  # только для демо-контура, для прода - вообще не влияет
            "amount": int(amount_rub * 100),  # копейки
            "invType": "READ_ONLY",
            "properties": [
                transaction_id,
            ],
            "bestBefore": str(deadline),
        }

        response = await self.request(
            method="POST",
            path="/api-shop/rs/open/invoice/create2",
            json=payload,
        )
        return response.text

    async def get_payments(self) -> list:
        response = await self.request(
            method="GET",
            path="/api-shop/rs/open/payments/new",
        )
        response_json = response.json()
        return response_json["payments"]
