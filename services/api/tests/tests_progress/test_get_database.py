import pytest

from httpx import AsyncClient


class TestGetUserProgressAPI:
    endpoint = "user-progress/{user_id}"

    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_get_user_progress(
        self,
        client: AsyncClient,
        user_login_fixture,
        user_resource_factory,
        game_constants_factory,
        user_level_factory,
        user_season_factory,
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
        await game_constants_factory()

        await user_level_factory(user_id=user_id, level_id=1)
        await user_season_factory(user_id=user_id, season_id=1)

        response = await client.get(
            self.endpoint.format(user_id=user_id),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response_json = response.json()
        seasons = response_json["seasons"]
        # print(seasons)

        for season in seasons:
            # season.pop("levels")
            print(season)

            for level in season["season"]["levels"]:
                print(level)

            print()
