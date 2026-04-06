import pytest

from httpx import AsyncClient


class TestCraftBonusCardAPI:
    endpoint = "user-progress/{user_id}/craft-bonus-cards"

    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_craft_bonus_cards(
        self,
        # service fixtures
        db_connection,
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
    ):
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        # запрос номер 1 - открываем карту id=1
        response = await client.post(
            self.endpoint.format(user_id=user_id),
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "cards_ids": [1]
            }
        )

        assert response.status_code == 200

        response_json = response.json()
        assert response_json == {'cards': {'1': {'user_card_id': 1, 'count': 1}}}

        # запрос номер 2 - повторный запрос! просто увеличим ей count
        response = await client.post(
            self.endpoint.format(user_id=user_id),
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "cards_ids": [1],
            }
        )

        assert response.status_code == 200

        response_json = response.json()
        assert response_json == {'cards': {'1': {'user_card_id': 1, 'count': 2}}}

        # запрос номер 3 - открываем карту id=2 и еще раз ту
        response = await client.post(
            self.endpoint.format(user_id=user_id),
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "cards_ids": [1, 2],
            }
        )

        assert response.status_code == 200

        response_json = response.json()
        assert response_json == {
            'cards': {
                # почему тут user_card_id=4, постгрес сделал до этого два insert on conflict update
                '1': {'user_card_id': 1, 'count': 3},
                '2': {'user_card_id': 4, 'count': 1},
            },
        }

        # запрос номер 4 - открываем карту id=3 и еще раз те
        response = await client.post(
            self.endpoint.format(user_id=user_id),
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "cards_ids": [1, 2, 3],
            }
        )

        assert response.status_code == 200

        response_json = response.json()
        assert response_json == {
            'cards': {
                '1': {'user_card_id': 1, 'count': 4},
                '2': {'user_card_id': 4, 'count': 2},
                '3': {'user_card_id': 7, 'count': 1},
            },
        }
