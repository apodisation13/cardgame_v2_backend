import pytest

from httpx import AsyncClient


class TestGetCardsAPI:
    endpoint = "cards"

    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_get_cards(
        self,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
    ):
        access_token = user_login_fixture["token"]["access_token"]

        response = await client.get(
            self.endpoint,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        response_json = response.json()

        expected_result = {
            "cards": [
                {
                    "id": 3,
                    "name": "Card 3",
                    "unlocked": False,
                    "faction": "Soldiers",
                    "type": "Special",
                    "color": "Gold",
                    "ability": {
                        "name": "Damage one",
                        "description": "Damage one",
                    },
                    "passive_ability": {
                        "name": "Passive ability",
                        "description": "Passive ability",
                    },
                    "data": {
                        "hp": 11,
                        "damage": 6,
                        "charges": 3,
                    },
                    "image": "http://test/media/player_cards/cards/3.webp",
                    "newly_added": False,
                },
                {
                    "id": 2,
                    "name": "Card 2",
                    "unlocked": True,
                    "faction": "Soldiers",
                    "type": "Special",
                    "color": "Silver",
                    "ability": {
                        "name": "Damage one",
                        "description": "Damage one",
                    },
                    "passive_ability": {
                        "name": None,
                        "description": None,
                    },
                    "data": {
                        "hp": 11,
                        "damage": 6,
                        "charges": 1,
                    },
                    "image": "http://test/media/player_cards/cards/2.webp",
                    "newly_added": False,
                },
                {
                    "id": 1,
                    "name": "Card 1",
                    "unlocked": True,
                    "faction": "Neutral",
                    "type": "Unit",
                    "color": "Bronze",
                    "ability": {
                        "name": "Damage one",
                        "description": "Damage one",
                    },
                    "passive_ability": {
                        "name": None,
                        "description": None,
                    },
                    "data": {
                        "hp": 10,
                        "damage": 5,
                        "charges": 2,
                        "passive": {"value": 10},
                    },
                    "image": "http://test/media/player_cards/cards/1.webp",
                    "newly_added": False,
                },
            ],
            "leaders": [
                {
                    "id": 1,
                    "name": "Leader 1",
                    "unlocked": True,
                    "faction": "Soldiers",
                    "ability": {
                        "name": "Damage one",
                        "description": "Damage one",
                    },
                    "passive_ability": {
                        "name": None,
                        "description": None,
                    },
                    "data": {
                        "hp": 10,
                        "damage": 5,
                        "passive": {"value": 10, "each_tick": True},
                    },
                    "image": "http://test/media/player_cards/leaders/1.webp",
                    "newly_added": False,
                },
            ],
            "enemies": {
                "1": {
                    "id": 1,
                    "name": "Enemy 1",
                    "faction": "Neutral",
                    "color": "Bronze",
                    "move": {
                        "name": "Down",
                        "description": "Down",
                    },
                    "passive_ability": {
                        "name": "Enemy passive ability",
                        "description": "Enemy passive ability",
                    },
                    "deathwish": {
                        "name": "Deathwish",
                        "description": "Deathwish",
                    },
                    "data": {
                        "hp": 10,
                        "damage": 5,
                        "passive": {"value": 10},
                    },
                    "image": "http://test/media/enemy_cards/enemies/1.webp",
                },
                "3": {
                    "id": 3,
                    "name": "Enemy 3",
                    "faction": "Soldiers",
                    "color": "Gold",
                    "move": {
                        "name": "Right",
                        "description": "Right",
                    },
                    "passive_ability": {
                        "name": None,
                        "description": None,
                    },
                    "deathwish": {
                        "name": None,
                        "description": None,
                    },
                    "data": {
                        "hp": 10,
                        "damage": 13,
                    },
                    "image": "http://test/media/enemy_cards/enemies/3.webp",
                },
                "2": {
                    "id": 2,
                    "name": "Enemy 2",
                    "faction": "Soldiers",
                    "color": "Silver",
                    "move": {
                        "name": "Right",
                        "description": "Right",
                    },
                    "passive_ability": {
                        "name": None,
                        "description": None,
                    },
                    "deathwish": {
                        "name": None,
                        "description": None,
                    },
                    "data": {
                        "hp": 10,
                        "damage": 3,
                    },
                    "image": "http://test/media/enemy_cards/enemies/2.webp",
                },
            },
            "enemy_leaders": {
                "1": {
                    "id": 1,
                    "name": "Enemy Leader 1",
                    "faction": "Neutral",
                    "ability": {
                        "name": "Enemy leader ability",
                        "description": "Enemy leader ability",
                    },
                    "passive_ability": {
                        "name": None,
                        "description": None,
                    },
                    "data": {
                        "hp": 10,
                        "passive": {"value": 10},
                    },
                    "image": "http://test/media/enemy_cards/enemy_leaders/1.webp",
                },
            },
        }

        assert response_json["enemies"] == expected_result["enemies"]
        assert response_json["enemy_leaders"] == expected_result["enemy_leaders"]
        assert response_json["cards"] == expected_result["cards"]
        assert response_json["leaders"] == expected_result["leaders"]

    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_get_cards_unauthorized(
        self,
        # service fixtures
        client: AsyncClient,
    ):
        response = await client.get(
            self.endpoint,
            headers={"Authorization": "Bearer some_token"},
        )
        assert response.status_code == 401
        response_json = response.json()
        assert response_json == {"detail": "Could not validate credentials"}

        response = await client.get(
            self.endpoint,
        )
        assert response.status_code == 401
        response_json = response.json()
        assert response_json == {"detail": "Missing authorization header"}
