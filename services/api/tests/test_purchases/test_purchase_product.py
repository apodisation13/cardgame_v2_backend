from unittest.mock import ANY

import pytest

from httpx import AsyncClient


class TestPurchaseProductAPI:
    endpoint = "/purchase-product/{product_id}"

    @pytest.mark.asyncio
    async def test_purchase_product_success(
        self,
        # service fixtures
        client: AsyncClient,
        db_connection,
        user_login_fixture,
        # fixtures for test
        product_factory,
    ):
        access_token = user_login_fixture["token"]["access_token"]
        user_id = user_login_fixture["id"]

        product = await product_factory()

        response = await client.post(
            self.endpoint.format(product_id=product.id),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        response_json = response.json()
        assert response_json == {
            "purchase_id": 1,
            "payment_url": "https://ckassa.ru/payment-link",
            "transaction_id": ANY,
        }

        purchases = await db_connection.fetch("""SELECT * FROM purchases""")
        assert len(purchases) == 1
        assert purchases[0]["id"] == 1
        assert purchases[0]["product_id"] == product.id
        assert purchases[0]["amount"] == product.price
        assert purchases[0]["user_id"] == user_id

        # никто не мешает повторно купить тот же продукт, создается новая покупка
        response = await client.post(
            self.endpoint.format(product_id=product.id),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        response_json = response.json()
        assert response_json == {
            "purchase_id": 2,
            "payment_url": "https://ckassa.ru/payment-link",
            "transaction_id": ANY,
        }

        purchases = await db_connection.fetch("""SELECT * FROM purchases ORDER BY updated_at DESC""")
        assert len(purchases) == 2
        assert purchases[0]["id"] == 2
        assert purchases[0]["product_id"] == product.id
        assert purchases[0]["amount"] == product.price
        assert purchases[0]["user_id"] == user_id

    @pytest.mark.asyncio
    async def test_purchase_product_failed(
        self,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        product_factory,
    ):
        access_token = user_login_fixture["token"]["access_token"]

        product = await product_factory(is_active=False)

        # нельзя купить неактивный продукт
        response = await client.post(
            self.endpoint.format(product_id=product.id),
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 404

        # нельзя купить несуществующий продукт
        response = await client.post(
            self.endpoint.format(product_id=2),
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 404
