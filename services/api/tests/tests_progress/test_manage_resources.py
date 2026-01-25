import pytest

from httpx import AsyncClient
from lib.utils.schemas.game import LevelDifficulty, ResourceActionSubtype
from services.api.app.apps.progress.schemas import UserResources


class TestManageResourcesAPI:
    endpoint = "user-progress/{user_id}/resource"

    @pytest.mark.parametrize(
        "difficulty, constant_name",
        (
            (LevelDifficulty.EASY, "play_level_easy"),
            (LevelDifficulty.NORMAL, "play_level_normal"),
            (LevelDifficulty.HARD, "play_level_hard"),
        ),
    )
    @pytest.mark.asyncio
    async def test_start_season_level(
        self,
        difficulty: LevelDifficulty,
        constant_name: str,
        client: AsyncClient,
        db_connection,
        init_db_cards,
        game_constants_factory,
        user_login_fixture,
        user_resource_factory,
    ):
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        user_resources = await user_resource_factory(id=user_id)

        game_constants = await game_constants_factory()
        play_level_price = game_constants.data[constant_name]  # -50, со знаком минус

        response = await client.patch(
            self.endpoint.format(user_id=user_id),
            json={
                "subtype": ResourceActionSubtype.START_SEASON_LEVEL,
                "data": {
                    "difficulty": difficulty,
                },
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response_json = response.json()

        assert response.status_code == 200
        assert (
            response_json
            == UserResources(
                scraps=user_resources.scraps,
                kegs=user_resources.kegs,
                big_kegs=user_resources.big_kegs,
                chests=user_resources.chests,
                wood=user_resources.wood + play_level_price,  # вот тут списали ресурсы за начало уровня
                keys=user_resources.keys,
            ).model_dump()
        )
