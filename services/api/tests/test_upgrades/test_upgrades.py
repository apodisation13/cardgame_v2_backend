import pytest
from httpx import AsyncClient

from lib.utils.schemas.game import DEFAULT_USER_UPGRADES, UpgradeType, UpgradeSubtype


class TestUserUpgradesAPI:
    endpoint = "user-upgrades/{user_id}"

    @pytest.mark.asyncio
    async def test_get_non_existing_upgrades(
        self,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
    ):
        """
        Тут у юзера еще нет сохраненных прокачек, и мы заинзертим ему новых (дефолтных)
        """
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        response = await client.get(
            self.endpoint.format(user_id=user_id),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response_json = response.json()
        assert response.status_code == 200
        assert response_json == DEFAULT_USER_UPGRADES

    @pytest.mark.asyncio
    async def test_get_already_existing_upgrades(
        self,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        user_upgrades_factory,
    ):
        """
        А тут у юзера уже есть какие-то прокачки, соответственно вернутся они
        """
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        upgrades = DEFAULT_USER_UPGRADES.copy()
        upgrades[UpgradeType.RESOURCES][UpgradeSubtype.MAX_CARDS_IN_DECK] = 1

        await user_upgrades_factory(
            id=user_id,
            data=upgrades,
        )

        response = await client.get(
            self.endpoint.format(user_id=user_id),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response_json = response.json()
        assert response.status_code == 200
        assert response_json == upgrades
