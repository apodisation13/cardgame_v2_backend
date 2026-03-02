import pytest

from httpx import AsyncClient
from lib.utils.schemas.game import CardActionSubtype


class TestManageCraftMillProcesAPI:
    endpoint = "user-progress/{user_id}/card/{card_id}"

    @pytest.mark.asyncio
    async def test_mill_leader_fails(
        self,
        client: AsyncClient,
        db_connection,
        init_db_cards,
        game_constants_factory,
        user_login_fixture,
        user_resource_factory,
        user_leader_factory,
        leader_factory,
    ):
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        # кейс 1 - такого лидера у юзера вообще нет
        response = await client.post(
            self.endpoint.format(user_id=user_id, card_id=1),
            json={
                "subtype": CardActionSubtype.MILL_LEADER,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400

        response_json = response.json()
        assert response_json["error"]["message"] == f"Cannot find such leader card 1 for user {user_id}"

        # кейс 2 - этот лидер открыт по умолчанию, его сейчас 1, его размиллить нельзя
        await user_leader_factory(leader_id=1, user_id=user_id)

        response = await client.post(
            self.endpoint.format(user_id=user_id, card_id=1),
            json={
                "subtype": CardActionSubtype.MILL_LEADER,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400

        response_json = response.json()
        assert response_json["error"]["message"] == f"Cannot mill default unlocked leader card 1 for user {user_id}"

        # кейс 3 - не хватает денег на милл лидера
        new_leader = await leader_factory(
            faction_id=1,
            ability_id=1,
            unlocked=False,
        )
        await user_leader_factory(leader_id=new_leader.id, user_id=user_id, count=1)
        await user_resource_factory(id=user_id, money=100)  # а там на милл нужно 200

        await game_constants_factory()

        response = await client.post(
            self.endpoint.format(user_id=user_id, card_id=new_leader.id),
            json={
                "subtype": CardActionSubtype.MILL_LEADER,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400

        response_json = response.json()
        assert response_json["error"]["message"] == f"User {user_id}, ACTUAL: -100 money"

        # кейс 4 - у юзера когда-то был этот лидер, потом стало 0, и его нельзя дальше миллить
        new_leader_2 = await leader_factory(
            faction_id=1,
            ability_id=1,
            unlocked=False,
        )
        await user_leader_factory(leader_id=new_leader_2.id, user_id=user_id, count=0)

        response = await client.post(
            self.endpoint.format(user_id=user_id, card_id=new_leader_2.id),
            json={
                "subtype": CardActionSubtype.MILL_LEADER,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400

        response_json = response.json()
        message = response_json["error"]["message"]
        assert message == f"Cannot mill leader card {new_leader_2.id} for user {user_id}, seems user doesn't have it"

    @pytest.mark.asyncio
    async def test_mill_leader_success(
        self,
        client: AsyncClient,
        db_connection,
        init_db_cards,
        game_constants_factory,
        user_login_fixture,
        user_resource_factory,
        user_leader_factory,
        leader_factory,
    ):
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        new_leader = await leader_factory(
            faction_id=1,
            ability_id=1,
            unlocked=False,
        )
        await user_leader_factory(
            leader_id=new_leader.id,
            user_id=user_id,
            count=2,
        )

        await user_resource_factory(
            id=user_id,
            money=400,
            scraps=1000,
        )

        await game_constants_factory()

        response = await client.post(
            self.endpoint.format(user_id=user_id, card_id=new_leader.id),
            json={
                "subtype": CardActionSubtype.MILL_LEADER,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        response_json = response.json()

        assert response_json["resources"]["scraps"] == 1000 + 500  # тут добавили +500 scraps
        assert response_json["resources"]["money"] == 400 - 200  # а тут отняли - 200 денег

        user_leaders = await db_connection.fetch("""SELECT * FROM user_leaders""")
        assert len(user_leaders) == 1
        assert user_leaders[0]["user_id"] == user_id
        assert user_leaders[0]["leader_id"] == new_leader.id
        assert user_leaders[0]["count"] == 1  # вот тут было 2 - стало 1

        # повторный запрос! теперь останется 0 лидеров и 0 денег
        response = await client.post(
            self.endpoint.format(user_id=user_id, card_id=new_leader.id),
            json={
                "subtype": CardActionSubtype.MILL_LEADER,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        response_json = response.json()

        assert response_json["resources"]["scraps"] == 1500 + 500  # тут добавили +500 scraps
        assert response_json["resources"]["money"] == 200 - 200  # а тут отняли - 200 денег, стало 0

        user_leaders = await db_connection.fetch("""SELECT * FROM user_leaders""")
        assert len(user_leaders) == 1
        assert user_leaders[0]["user_id"] == user_id
        assert user_leaders[0]["leader_id"] == new_leader.id
        assert user_leaders[0]["count"] == 0  # вот тут было 1 - а стало вообще 0

    @pytest.mark.asyncio
    async def test_mill_card_fails(
        self,
        client: AsyncClient,
        db_connection,
        init_db_cards,
        game_constants_factory,
        user_login_fixture,
        user_resource_factory,
        user_card_factory,
        card_factory,
    ):
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        # кейс 1 - такой карты у юзера вообще нет
        response = await client.post(
            self.endpoint.format(user_id=user_id, card_id=17),
            json={
                "subtype": CardActionSubtype.MILL_CARD,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400

        response_json = response.json()
        assert response_json["error"]["message"] == f"Cannot find such card 17 for user {user_id}"

        # кейс 2 - эта карта открыта по умолчанию, ее сейчас 1, и ее размиллить нельзя
        await user_card_factory(card_id=1, user_id=user_id)

        response = await client.post(
            self.endpoint.format(user_id=user_id, card_id=1),
            json={
                "subtype": CardActionSubtype.MILL_CARD,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400

        response_json = response.json()
        assert response_json["error"]["message"] == f"Cannot mill default unlocked card 1 for user {user_id}"

        # кейс 3 - не хватает денег на милл карты
        await user_card_factory(card_id=3, user_id=user_id, count=1)
        await user_resource_factory(id=user_id, money=100)  # а там на милл нужно всегда 200

        await game_constants_factory()

        response = await client.post(
            self.endpoint.format(user_id=user_id, card_id=3),
            json={
                "subtype": CardActionSubtype.MILL_CARD,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400

        response_json = response.json()
        assert response_json["error"]["message"] == f"User {user_id}, ACTUAL: -100 money"

        # кейс 4 - у юзера когда-то была эта карта, потом стало 0, и ее нельзя дальше миллить
        new_card = await card_factory(
            faction_id=1,
            ability_id=1,
            color_id=1,
            type_id=1,
            unlocked=False,
        )
        await user_card_factory(card_id=new_card.id, user_id=user_id, count=0)

        response = await client.post(
            self.endpoint.format(user_id=user_id, card_id=new_card.id),
            json={
                "subtype": CardActionSubtype.MILL_CARD,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400

        response_json = response.json()
        message = response_json["error"]["message"]
        assert message == f"Cannot mill card {new_card.id} for user {user_id}, seems user doesn't have it"