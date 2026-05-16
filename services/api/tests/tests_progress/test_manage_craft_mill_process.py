import pytest

from httpx import AsyncClient
from lib.utils.schemas.game import CardActionSubtype, ResourceType


class TestManageMillProcesAPI:
    endpoint = "user-progress/{user_id}/card/{card_id}"

    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_mill_leader_fails(
        self,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        game_constants_factory,
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
        assert response_json["error"]["message"] == f"Cannot find such leader 1 for user {user_id}"

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
        assert response_json["error"]["message"] == f"Cannot mill default unlocked leader 1 for user {user_id}"

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
        assert response_json["error"]["message"] == f"Scenario: Subtype mill_leader, user_id: {user_id}, resource: {ResourceType.MONEY} - insufficient resources (actual: {100-200})"

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
        assert message == f"Cannot mill leader {new_leader_2.id} for user {user_id}, seems user doesn't have it"

    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_mill_leader_success(
        self,
        # service fixtures
        client: AsyncClient,
        db_connection,
        user_login_fixture,
        # fixtures for test
        game_constants_factory,
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

    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_mill_card_fails(
        self,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        game_constants_factory,
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
        assert response_json["error"]["message"] == f"Scenario: Subtype mill_card, user_id: {user_id}, resource: {ResourceType.MONEY} - insufficient resources (actual: {100-200})"

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

    @pytest.mark.parametrize(
        "card_color, expected_resource_type, expected_scarps_add",
        (
            (1, ResourceType.BRONZE_INGOTS, 100),
            (2, ResourceType.SILVER_INGOTS, 250),
            (3, ResourceType.GOLD_INGOTS, 500),
        ),
    )
    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_mill_card_success(
        self,
        card_color,
        expected_resource_type,
        expected_scarps_add,
        # service fixtures
        client: AsyncClient,
        db_connection,
        user_login_fixture,
        # fixtures for test
        game_constants_factory,
        user_resource_factory,
        user_card_factory,
        card_factory,
    ):
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        new_card = await card_factory(
            faction_id=1,
            ability_id=1,
            color_id=card_color,
            type_id=1,
            unlocked=False,
        )
        await user_card_factory(
            card_id=new_card.id,
            user_id=user_id,
            count=2,  # 2 такие карты есть сейчас
        )

        await user_resource_factory(
            id=user_id,
            money=400,
            scraps=1000,
            bronze_ingots=0,
            silver_ingots=0,
            gold_ingots=0,
        )

        await game_constants_factory()

        response = await client.post(
            self.endpoint.format(user_id=user_id, card_id=new_card.id),
            json={
                "subtype": CardActionSubtype.MILL_CARD,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        response_json = response.json()

        assert response_json["resources"]["scraps"] == 1000 + expected_scarps_add  # в зависимости от цвета карты
        assert response_json["resources"]["money"] == 400 - 200  # а тут отняли -200 денег в любом случае
        assert response_json["resources"][expected_resource_type] == 1  # было 0, стало 1, по цвету тоже

        user_cards = await db_connection.fetch("""SELECT * FROM user_cards""")
        assert len(user_cards) == 1
        assert user_cards[0]["user_id"] == user_id
        assert user_cards[0]["card_id"] == new_card.id
        assert user_cards[0]["count"] == 1  # вот тут было 2 - стало 1

        # повторный запрос! теперь останется 0 лидеров и 0 денег
        response = await client.post(
            self.endpoint.format(user_id=user_id, card_id=new_card.id),
            json={
                "subtype": CardActionSubtype.MILL_CARD,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        response_json = response.json()

        assert response_json["resources"]["scraps"] == 1000 + expected_scarps_add * 2
        assert response_json["resources"]["money"] == 0
        assert response_json["resources"][expected_resource_type] == 2  # было 0, стало 2, по цвету тоже

        user_cards = await db_connection.fetch("""SELECT * FROM user_cards""")
        assert len(user_cards) == 1
        assert user_cards[0]["user_id"] == user_id
        assert user_cards[0]["card_id"] == new_card.id
        assert user_cards[0]["count"] == 0  # вот тут было 2 - стало 1


class TestManageCraftProcesAPI:
    endpoint = "user-progress/{user_id}/card/{card_id}"

    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_craft_leader_fails(
        self,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        game_constants_factory,
        user_resource_factory,
    ):
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        await game_constants_factory()

        await user_resource_factory(
            id=user_id,
            money=2000,
            scraps=1000,
            bronze_ingots=1,
            silver_ingots=0,  # вот этой не хватает, но достаточно хотя бы одной чтобы не хватало, и все упадет
            gold_ingots=1,
        )

        # кейс 1 - не хватает ресурсов для крафта
        response = await client.post(
            self.endpoint.format(user_id=user_id, card_id=1),
            json={
                "subtype": CardActionSubtype.CRAFT_LEADER,
                "recipe": {
                    ResourceType.SCRAPS: -1000,
                    ResourceType.BRONZE_INGOTS: -1,
                    ResourceType.SILVER_INGOTS: -1,
                    ResourceType.GOLD_INGOTS: -1,
                    ResourceType.MONEY: -2000,
                },
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400

        response_json = response.json()
        assert response_json["error"]["message"] == f"Scenario: Subtype craft_leader, user_id: {user_id}, resource: {ResourceType.SILVER_INGOTS} - insufficient resources (actual: {0-1})"

        # кейс 2 - прислали recipe, которого нет в конфиге
        recipe = {
            ResourceType.SCRAPS: 123456,  # или левый recipe вообще
            ResourceType.BRONZE_INGOTS: -1,
            ResourceType.SILVER_INGOTS: -1,
            ResourceType.GOLD_INGOTS: -1,
            ResourceType.MONEY: -2000,
        }

        response = await client.post(
            self.endpoint.format(user_id=user_id, card_id=1),
            json={
                "subtype": CardActionSubtype.CRAFT_LEADER,
                "recipe": recipe,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400

        response_json = response.json()
        assert "Craft leader error: no config for recipe" in response_json["error"]["message"]

    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_craft_leader_success(
        self,
        # service fixtures
        client: AsyncClient,
        db_connection,
        user_login_fixture,
        # fixtures for test
        game_constants_factory,
        user_resource_factory,
        user_leader_factory,
        leader_factory,
    ):
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        await user_leader_factory(leader_id=1, user_id=user_id)

        await game_constants_factory()

        await user_resource_factory(
            id=user_id,
            money=10000,
            scraps=3000,
            bronze_ingots=3,
            silver_ingots=3,
            gold_ingots=3,
            raw_bronze=45,
            raw_silver=45,
            raw_gold=45,
            rare_gem=1,
        )

        # кейс 1 - крафтим того, который уже есть
        response = await client.post(
            self.endpoint.format(user_id=user_id, card_id=1),
            json={
                "subtype": CardActionSubtype.CRAFT_LEADER,
                "recipe": {
                    ResourceType.SCRAPS: -1000,
                    ResourceType.BRONZE_INGOTS: -1,
                    ResourceType.SILVER_INGOTS: -1,
                    ResourceType.GOLD_INGOTS: -1,
                    ResourceType.MONEY: -2000,
                },
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        response_json = response.json()

        user_leaders = await db_connection.fetch("""SELECT * FROM user_leaders""")
        assert len(user_leaders) == 1
        assert user_leaders[0]["leader_id"] == 1
        assert user_leaders[0]["count"] == 2  # он же уже был у юзера как открытый по умолчанию

        assert response_json["resources"]["scraps"] == 2000
        assert response_json["resources"]["money"] == 8000
        assert response_json["resources"]["bronze_ingots"] == 2
        assert response_json["resources"]["silver_ingots"] == 2
        assert response_json["resources"]["gold_ingots"] == 2

        # кейс 2 - крафтим того же, но с другой формулой для крафта
        response = await client.post(
            self.endpoint.format(user_id=user_id, card_id=1),
            json={
                "subtype": CardActionSubtype.CRAFT_LEADER,
                "recipe": {
                    ResourceType.SCRAPS: -1000,
                    ResourceType.RAW_BRONZE: -15,
                    ResourceType.RAW_SILVER: -15,
                    ResourceType.RAW_GOLD: -15,
                    ResourceType.MONEY: -2000,
                },
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        response_json = response.json()

        user_leaders = await db_connection.fetch("""SELECT * FROM user_leaders""")
        assert len(user_leaders) == 1
        assert user_leaders[0]["leader_id"] == 1
        assert user_leaders[0]["count"] == 3  # еще единичку прибавили

        assert response_json["resources"]["scraps"] == 1000
        assert response_json["resources"]["money"] == 6000
        assert response_json["resources"]["bronze_ingots"] == 2  # эти не изменились, мы крафтили из другого
        assert response_json["resources"]["silver_ingots"] == 2
        assert response_json["resources"]["gold_ingots"] == 2
        assert response_json["resources"]["raw_bronze"] == 30  # теперь изменились вот эти
        assert response_json["resources"]["raw_silver"] == 30
        assert response_json["resources"]["raw_gold"] == 30

        # кейс 3 - крафтим нового лидера, с третьей доступной формулой

        new_leader = await leader_factory(
            faction_id=1,
            ability_id=1,
            unlocked=False,
        )
        response = await client.post(
            self.endpoint.format(user_id=user_id, card_id=new_leader.id),
            json={
                "subtype": CardActionSubtype.CRAFT_LEADER,
                "recipe": {
                    ResourceType.RARE_GEM: -1,
                },
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        response_json = response.json()

        user_leaders = await db_connection.fetch("""SELECT * FROM user_leaders ORDER BY updated_at DESC""")
        assert len(user_leaders) == 2  # тут вот новый открылся
        assert user_leaders[1]["leader_id"] == 1  # это тот который был, он последний в списке
        assert user_leaders[1]["count"] == 3

        assert user_leaders[0]["leader_id"] == new_leader.id  # это новый, которого скрафтили
        assert user_leaders[0]["count"] == 1

        assert response_json["resources"]["rare_gem"] == 0  # вот его-то и стало 0

        assert response_json["resources"]["scraps"] == 1000  # здесь ничего не изменилось, кроме rare_gem
        assert response_json["resources"]["money"] == 6000
        assert response_json["resources"]["bronze_ingots"] == 2
        assert response_json["resources"]["silver_ingots"] == 2
        assert response_json["resources"]["gold_ingots"] == 2
        assert response_json["resources"]["raw_bronze"] == 30
        assert response_json["resources"]["raw_silver"] == 30
        assert response_json["resources"]["raw_gold"] == 30

    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_craft_card_fails(
        self,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        game_constants_factory,
        user_resource_factory,
    ):
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        await game_constants_factory()

        await user_resource_factory(
            id=user_id,
            money=2000,
            scraps=1000,
            raw_bronze=0,
        )

        # кейс 1 - не хватает ресурсов для крафта
        response = await client.post(
            self.endpoint.format(user_id=user_id, card_id=1),
            json={
                "subtype": CardActionSubtype.CRAFT_CARD,
                "recipe": {
                    ResourceType.SCRAPS: -250,
                    ResourceType.RAW_BRONZE: -50,  # вот этой не хватает
                    ResourceType.MONEY: -500,
                },
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400

        response_json = response.json()
        assert response_json["error"]["message"] == f"Scenario: Subtype craft_card, user_id: {user_id}, resource: {ResourceType.RAW_BRONZE} - insufficient resources (actual: {0-50})"

        # кейс 2 - прислали recipe, которого нет в конфиге
        recipe = {
            ResourceType.SCRAPS: 123456,  # или левый recipe вообще
            ResourceType.BRONZE_INGOTS: -1,
            ResourceType.SILVER_INGOTS: -1,
            ResourceType.GOLD_INGOTS: -1,
            ResourceType.MONEY: -2000,
        }

        response = await client.post(
            self.endpoint.format(user_id=user_id, card_id=1),
            json={
                "subtype": CardActionSubtype.CRAFT_CARD,
                "recipe": recipe,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400

        response_json = response.json()
        assert "Craft card error: no config for recipe" in response_json["error"]["message"]

    @pytest.mark.parametrize(
        "card_color, recipe",
        (
            (
                1,
                {
                    ResourceType.SCRAPS: -250,
                    ResourceType.RAW_BRONZE: -50,
                    ResourceType.MONEY: -500,
                },
            ),
            (
                1,
                {
                    ResourceType.SCRAPS: -250,
                    ResourceType.BRONZE_INGOTS: -3,
                    ResourceType.MONEY: -500,
                },
            ),
            (
                1,
                {
                    ResourceType.RARE_GEM: -1,
                },
            ),
            (
                2,
                {
                    ResourceType.SCRAPS: -1000,
                    ResourceType.RAW_SILVER: -50,
                    ResourceType.MONEY: -1000,
                },
            ),
            (
                3,
                {
                    ResourceType.SCRAPS: -2000,
                    ResourceType.RAW_GOLD: -50,
                    ResourceType.MONEY: -2000,
                },
            ),
        ),
    )
    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_craft_card_success(
        self,
        card_color,
        recipe,
        # service fixtures
        client: AsyncClient,
        db_connection,
        user_login_fixture,
        # fixtures for test
        game_constants_factory,
        user_resource_factory,
        user_card_factory,
        card_factory,
    ):
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        new_card = await card_factory(
            faction_id=1,
            ability_id=1,
            color_id=card_color,
            type_id=1,
            unlocked=False,
        )

        user_resources = await user_resource_factory(
            id=user_id,
            money=4000,
            scraps=2000,
            raw_bronze=2000,
            raw_silver=300,
            raw_gold=400,
            bronze_ingots=3,
            rare_gem=1,
        )

        await game_constants_factory()

        # 1й запрос - карты еще нету у юзера
        response = await client.post(
            self.endpoint.format(user_id=user_id, card_id=new_card.id),
            json={
                "subtype": CardActionSubtype.CRAFT_CARD,
                "recipe": recipe,
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        response_json = response.json()
        user_resources_after = response_json["resources"]

        for resource, value in recipe.items():
            assert user_resources_after[resource] == getattr(user_resources, resource) + value

        user_cards = await db_connection.fetch("""SELECT * FROM user_cards""")
        assert len(user_cards) == 1  # вот тут появилась новая карта у юзера
        assert user_cards[0]["card_id"] == new_card.id
        assert user_cards[0]["count"] == 1
