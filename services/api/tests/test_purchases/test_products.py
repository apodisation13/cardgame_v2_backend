import pytest

from httpx import AsyncClient

from lib.utils.schemas.game import ResourceType
from lib.utils.schemas.products import ProductType


class TestProductsAPI:
    endpoint = "/products"

    @pytest.mark.asyncio
    async def test_get_all_products(
        self,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
        product_factory,
    ):
        access_token = user_login_fixture["token"]["access_token"]

        response = await client.get(
            self.endpoint,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        response_json = response.json()
        assert response_json == []

        await product_factory(
            is_active=False,
        )
        product_2 = await product_factory(
            is_active=True,
            priority=1,
            price=134.23,
            data={"resources": {ResourceType.MONEY: 20000}},
        )
        product_3 = await product_factory(
            is_active=True,
            priority=5,
            price=334.21,
        )
        product_4 = await product_factory(
            is_active=True,
            priority=5,
            price=234.21,
        )

        response = await client.get(
            self.endpoint,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        response_json = response.json()

        expected_data = [
            {
                "id": product_4.id,
                "title": "title",
                "data": {
                    "resources": {
                        ResourceType.MONEY: 2000,
                        ResourceType.WOOD: 1000,
                        ResourceType.SCRAPS: 1500,
                    },
                },
                "type": ProductType.RESOURCE,
                "price": 234.21,
            },
            {
                "id": product_3.id,
                "title": "title",
                "data": {
                    "resources": {
                        ResourceType.MONEY: 2000,
                        ResourceType.WOOD: 1000,
                        ResourceType.SCRAPS: 1500,
                    },
                },
                "type": ProductType.RESOURCE,
                "price": 334.21,
            },
            {
                "id": product_2.id,
                "title": "title",
                "data": {"resources": {ResourceType.MONEY: 20000}},
                "type": ProductType.RESOURCE,
                "price": 134.23,
            },
        ]

        assert response_json == expected_data
