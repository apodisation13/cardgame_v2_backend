import pytest

from httpx import AsyncClient
from services.api.app.apps.progress.schemas import UserResources


class TestGetUserResourcesAPI:
    endpoint = "user-progress/{user_id}/resource"

    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_get_user_resources(
        self,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        user_resource_factory,
    ):
        """
        Базовая фикстура добавила уже 3 разных уровня
        У юзера открыт уровень id=4
        У этого уровня нет связанных уровней (level_related_levels)
        Соответственно если юзер проходит этот уровень, то ему мы поставим finished
        И всё, открывать новые не надо, их ведь нет
        Если уровень УЖЕ пройден, ничего страшного, так и останется
        """
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        await user_resource_factory(id=user_id)

        response = await client.get(
            self.endpoint.format(user_id=user_id),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response_json = response.json()

        assert (
            response_json
            == UserResources(
                scraps=1000,
                raw_bronze=0,
                raw_silver=0,
                raw_gold=0,
                bronze_ingots=0,
                silver_ingots=0,
                gold_ingots=0,
                crops=1000,
                wood=1000,
                silk=0,
                kegs=3,
                big_kegs=1,
                chests=0,
                keys=3,
                rare_gem=0,
                money=2000,
                flowers=0,
                first_aid_kits=0,
                shields=0,
            ).model_dump()
        )
