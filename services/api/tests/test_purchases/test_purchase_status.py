import pytest

from httpx import AsyncClient
from lib.utils.schemas.products import PurchaseStatus


class TestPurchaseStatusAPI:
    endpoint = "/purchase-status/{purchase_id}"

    @pytest.mark.asyncio
    async def test_get_purchase_status(
        self,
        # service fixtures
        client: AsyncClient,
        db_connection,
        user_login_fixture,
        # fixtures for test
        product_factory,
        purchase_factory,
    ):
        access_token = user_login_fixture["token"]["access_token"]
        user_id = user_login_fixture["id"]

        product = await product_factory()
        purchase = await purchase_factory(product_id=product.id, user_id=user_id)

        response = await client.get(
            self.endpoint.format(purchase_id=purchase.id),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        response_json = response.json()
        assert response_json == PurchaseStatus.PENDING

        await db_connection.execute(
            """UPDATE purchases SET status = $1 WHERE id = $2;""",
            PurchaseStatus.SUCCESS,
            purchase.id,
        )

        response = await client.get(
            self.endpoint.format(purchase_id=purchase.id),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        response_json = response.json()
        assert response_json == PurchaseStatus.SUCCESS

        # попытка вызвать несуществующую покупку
        response = await client.get(
            self.endpoint.format(purchase_id=2),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404
        response_json = response.json()
        assert response_json == {
            "error": {
                "code": "NOT_FOUND",
                "message": "PurchaseDoesNotExistError",
                "details": "PurchaseDoesNotExistError()",
            },
        }
