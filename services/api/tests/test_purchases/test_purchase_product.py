import pytest

from httpx import AsyncClient


class TestPurchaseProductAPI:
    endpoint = "user/{user_id}/purchase-product/{product_id}"

    @pytest.mark.asyncio
    async def test_purchase_product_success(
        self,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        product_factory,
    ):
        access_token = user_login_fixture["token"]["access_token"]
        user_id = user_login_fixture["id"]

        product = await product_factory()

        response = await client.post(
            self.endpoint.format(user_id=user_id, product_id=product.id),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        response_json = response.json()
        assert response_json == {
            "purchase_id": 1,
            "confirmation_url": None,
        }

        # никто не мешает повторно купить тот же продукт, создается новая покупка
        response = await client.post(
            self.endpoint.format(user_id=user_id, product_id=product.id),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        response_json = response.json()
        assert response_json == {
            "purchase_id": 2,
            "confirmation_url": None,
        }

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
        user_id = user_login_fixture["id"]

        product = await product_factory(is_active=False)

        # нельзя купить неактивный продукт
        response = await client.post(
            self.endpoint.format(user_id=user_id, product_id=product.id),
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 404

        # нельзя купить несуществующий продукт
        response = await client.post(
            self.endpoint.format(user_id=user_id, product_id=2),
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 404
