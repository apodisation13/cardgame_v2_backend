import pytest

from httpx import AsyncClient
from lib.utils.schemas.game import UserStatsRecordType


class TestGetUserStatsAPI:
    endpoint = "statistics/{user_id}/stats"

    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_get_self_stats(
        self,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        user_stats_factory,
        faction_factory,
        user_card_factory,
        user_leader_factory,
        user_level_factory,
        user_season_factory,
    ):
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        # -------------- 1й запрос - юзер еще не играл --------------
        response = await client.get(
            self.endpoint.format(user_id=user_id),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response_json = response.json()
        assert response.status_code == 200

        assert response_json == {
            "stats": {
                "Soldiers": {"play": 0, "win": 0, "winrate": 0},
            },
            "cards": {"total": 3, "open": 0},
            "leaders": {"total": 1, "open": 0},
            "seasons": {"total": 2, "finished": 0},
            "levels": {"total": 4, "finished": 0},
        }

        await user_stats_factory(
            user_id=user_id,
            faction_id=1,  # если каким-то образом даже в эту таблицу попали нейтралки, они не считаются
            type=UserStatsRecordType.PLAY,
            count=2,
        )
        await user_stats_factory(
            user_id=user_id,
            faction_id=2,
            type=UserStatsRecordType.PLAY,
            count=2,
        )
        await user_stats_factory(
            user_id=user_id,
            faction_id=2,
            type=UserStatsRecordType.WIN,
            count=1,
        )

        # -------------- 2й запрос - юзер сыграл 2 игры, выиграл 1 --------------
        response = await client.get(
            self.endpoint.format(user_id=user_id),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response_json = response.json()
        assert response.status_code == 200

        assert response_json == {
            "stats": {
                "Soldiers": {"play": 2, "win": 1, "winrate": 50},
            },
            "cards": {"total": 3, "open": 0},
            "leaders": {"total": 1, "open": 0},
            "seasons": {"total": 2, "finished": 0},
            "levels": {"total": 4, "finished": 0},
        }

        # -------------- 3й запрос - юзер сыграл новой фракцией --------------

        # новая фракция в этом тесте
        f3 = await faction_factory(name="Monsters")
        await user_stats_factory(
            user_id=user_id,
            faction_id=f3.id,
            type=UserStatsRecordType.PLAY,
            count=3,
        )
        await user_stats_factory(
            user_id=user_id,
            faction_id=f3.id,
            type=UserStatsRecordType.WIN,
            count=2,
        )

        response = await client.get(
            self.endpoint.format(user_id=user_id),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response_json = response.json()
        assert response.status_code == 200

        assert response_json == {
            "stats": {
                "Soldiers": {"play": 2, "win": 1, "winrate": 50},
                "Monsters": {"play": 3, "win": 2, "winrate": 66.7},
            },
            "cards": {"total": 3, "open": 0},
            "leaders": {"total": 1, "open": 0},
            "seasons": {"total": 2, "finished": 0},
            "levels": {"total": 4, "finished": 0},
        }

    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_get_stats_for_another_user(
        self,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        user_factory,
        user_card_factory,
        user_level_factory,
    ):
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        # -------------- 1й запрос - а такого юзера нет, для которого мы запрашиваем --------------
        response = await client.get(
            f"{self.endpoint.format(user_id=user_id)}?for_user=5",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response_json = response.json()
        assert response.status_code == 400

        assert response_json == {
            "error": {
                "code": "BAD_REQUEST",
                "details": "UserNotFoundError()",
                "message": "",
            },
        }

        new_user = await user_factory()

        # -------------- 2й запрос - действительно есть такой юзер --------------
        response = await client.get(
            f"{self.endpoint.format(user_id=user_id)}?for_user={new_user.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response_json = response.json()
        assert response.status_code == 200

        assert response_json == {
            "stats": {
                "Soldiers": {"play": 0, "win": 0, "winrate": 0},
            },
            "cards": {"total": 3, "open": 0},
            "leaders": {"total": 1, "open": 0},
            "seasons": {"total": 2, "finished": 0},
            "levels": {"total": 4, "finished": 0},
        }

        # а тут у юзера появилась одна карта и один уровень пройден
        await user_card_factory(
            user_id=new_user.id,
            card_id=1,
        )
        await user_level_factory(
            user_id=new_user.id,
            level_id=1,
            finished=True,
        )

        # -------------- 3й запрос - статистика уже верна --------------
        response = await client.get(
            f"{self.endpoint.format(user_id=user_id)}?for_user={new_user.id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response_json = response.json()
        assert response.status_code == 200

        assert response_json == {
            "stats": {
                "Soldiers": {"play": 0, "win": 0, "winrate": 0},
            },
            "cards": {"total": 3, "open": 1},
            "leaders": {"total": 1, "open": 0},
            "seasons": {"total": 2, "finished": 0},
            "levels": {"total": 4, "finished": 1},
        }


class TestPostUserStatsAPI:
    endpoint = "statistics/{user_id}/stats"

    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_post_stats(
        self,
        # service fixtures
        db_connection,
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        user_deck_factory,
    ):
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        # базовая колода фракции 1
        user_deck = await user_deck_factory(
            user_id=user_id,
            deck_id=1,
        )

        # -------------- 1й запрос - юзер еще не играл ранее --------------
        response = await client.post(
            self.endpoint.format(user_id=user_id),
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "user_deck_id": user_deck.id,
                "type": UserStatsRecordType.PLAY,
            },
        )

        response_json = response.json()
        assert response.status_code == 200

        assert response_json == {"200": "OK"}

        user_stats = await db_connection.fetch("SELECT * FROM user_stats")

        assert len(user_stats) == 1

        assert user_stats[0]["user_id"] == user_id
        assert user_stats[0]["faction_id"] == 2
        assert user_stats[0]["count"] == 1
        assert user_stats[0]["type"] == UserStatsRecordType.PLAY

        # -------------- 2й запрос - еще раз играет --------------
        response = await client.post(
            self.endpoint.format(user_id=user_id),
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "user_deck_id": user_deck.id,
                "type": UserStatsRecordType.PLAY,
            },
        )

        response_json = response.json()
        assert response.status_code == 200

        assert response_json == {"200": "OK"}

        # тут не добавилось новых записей, так как там ON CONFLICT
        user_stats = await db_connection.fetch("SELECT * FROM user_stats")

        assert len(user_stats) == 1

        assert user_stats[0]["user_id"] == user_id
        assert user_stats[0]["faction_id"] == 2
        assert user_stats[0]["count"] == 2
        assert user_stats[0]["type"] == UserStatsRecordType.PLAY

        # -------------- 3й запрос - он выиграл --------------
        response = await client.post(
            self.endpoint.format(user_id=user_id),
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "user_deck_id": user_deck.id,
                "type": UserStatsRecordType.WIN,
            },
        )

        response_json = response.json()
        assert response.status_code == 200

        assert response_json == {"200": "OK"}

        # а вот тут добавилась новая запись, с новым типом
        user_stats = await db_connection.fetch("SELECT * FROM user_stats ORDER BY updated_at DESC")

        assert len(user_stats) == 2

        assert user_stats[0]["count"] == 1
        assert user_stats[0]["type"] == UserStatsRecordType.WIN
        assert user_stats[1]["count"] == 2
        assert user_stats[1]["type"] == UserStatsRecordType.PLAY

        # -------------- проверяем расчет статистики --------------
        response = await client.get(
            self.endpoint.format(user_id=user_id),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response_json = response.json()
        assert response.status_code == 200

        assert response_json == {
            "stats": {
                "Soldiers": {"play": 2, "win": 1, "winrate": 50},
            },
            "cards": {"total": 3, "open": 0},
            "leaders": {"total": 1, "open": 0},
            "seasons": {"total": 2, "finished": 0},
            "levels": {"total": 4, "finished": 0},
        }
