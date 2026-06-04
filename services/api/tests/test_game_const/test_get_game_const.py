from unittest.mock import ANY

import pytest

from httpx import AsyncClient


class TestGetGameConstAPI:
    endpoint = "game_const"

    @pytest.mark.asyncio
    async def test_get_game_const(
        self,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        game_constants_factory,
    ):
        access_token = user_login_fixture["token"]["access_token"]

        response = await client.get(
            self.endpoint,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        response_json = response.json()
        assert response_json == {}

        await game_constants_factory()

        response = await client.get(
            self.endpoint,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        response_json = response.json()
        assert response_json == {
            "max_random_n_enemies": 200,
            "resources_transitions": ANY,
            "key_rewards": ANY,
            "win_level_rewards": ANY,
            "start_level_prices": ANY,
            "cards_resources_prices": ANY,
            "upgrades": ANY,
            "arena_upgrades": ANY,
        }
