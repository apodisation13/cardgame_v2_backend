import copy

import pytest

from httpx import AsyncClient
from lib.utils.schemas.game import (
    DEFAULT_RESOURCES_TRANSITIONS,
    DEFAULT_USER_UPGRADES,
    ResourceActionSubtype,
    ResourceTransitionActionType,
    ResourceType,
    UpgradeSubtype,
    UpgradeType,
)
from services.api.app.apps.progress.schemas import UserResources


class TestManageResourcesLevelStartWinAPI:
    endpoint = "user-progress/{user_id}/resource"

    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_start_season_level_success(
        self,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        user_resource_factory,
    ):
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        user_resources = await user_resource_factory(id=user_id)

        response = await client.patch(
            self.endpoint.format(user_id=user_id),
            json={
                "subtype": ResourceActionSubtype.START_SEASON_LEVEL,
                "data": {
                    ResourceType.CROPS: -300,
                    ResourceType.WOOD: -200,
                    ResourceType.MONEY: -1000,
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
                raw_bronze=0,
                raw_silver=0,
                raw_gold=0,
                bronze_ingots=0,
                silver_ingots=0,
                gold_ingots=0,
                crops=user_resources.crops - 300,
                wood=user_resources.wood - 200,
                silk=0,
                kegs=user_resources.kegs,
                big_kegs=user_resources.big_kegs,
                chests=user_resources.chests,
                keys=user_resources.keys,
                rare_gem=0,
                money=user_resources.money - 1000,
            ).model_dump()
        )

    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_start_season_level_fails(
        self,
        # service fixtures
        client: AsyncClient,
        db_connection,
        user_login_fixture,
        # fixtures for test
        user_resource_factory,
    ):
        subtype = ResourceActionSubtype.START_SEASON_LEVEL

        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        await user_resource_factory(
            id=user_id,
            money=200,
            crops=500,
            wood=500,
        )

        # кейс 1 - не хватает ресурсов для начала уровня
        response = await client.patch(
            self.endpoint.format(user_id=user_id),
            json={
                "subtype": subtype,
                "data": {
                    ResourceType.CROPS: -300,
                    ResourceType.WOOD: -200,
                    ResourceType.MONEY: -1000,  # не хватит денег для игры
                },
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400

        response_json = response.json()
        message = response_json["error"]["message"]
        assert (
            message == f"Scenario: Manage resources: subtype {subtype},"
            f" user_id: {user_id},"
            f" resource: {ResourceType.MONEY} - insufficient resources (actual: {200 - 1000})"
        )

        # кейс 2 - грязный хак через постман - накручиваем положительные ресурсы
        response = await client.patch(
            self.endpoint.format(user_id=user_id),
            json={
                "subtype": subtype,
                "data": {
                    ResourceType.MONEY: 300,
                },
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400

        response_json = response.json()
        message = response_json["error"]["message"]
        assert message == f"Can not process subtype {subtype} for user {user_id}, wrong value: {300} money"

        resources_left = await db_connection.fetchrow("""SELECT * FROM user_resources WHERE id = $1""", user_id)
        assert resources_left["crops"] == 500
        assert resources_left["wood"] == 500
        assert resources_left["money"] == 200

    @pytest.mark.parametrize(
        "subtype",
        (
            ResourceActionSubtype.WIN_SEASON_LEVEL,
            ResourceActionSubtype.ACCEPT_KEY_REWARD,
        ),
    )
    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_win_season_level_or_accept_key_reward(
        self,
        subtype: ResourceActionSubtype,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        user_upgrades_factory,
        user_resource_factory,
    ):
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        await user_upgrades_factory(id=user_id)

        user_resources = await user_resource_factory(id=user_id)

        response = await client.patch(
            self.endpoint.format(user_id=user_id),
            json={
                "subtype": subtype,
                "data": {
                    ResourceType.CROPS: 1111,
                    ResourceType.WOOD: 200,
                    ResourceType.MONEY: 1000,
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
                raw_bronze=0,
                raw_silver=0,
                raw_gold=0,
                bronze_ingots=0,
                silver_ingots=0,
                gold_ingots=0,
                crops=user_resources.crops + 1111,
                wood=user_resources.wood + 200,
                silk=0,
                kegs=user_resources.kegs,
                big_kegs=user_resources.big_kegs,
                chests=user_resources.chests,
                keys=user_resources.keys,
                rare_gem=0,
                money=user_resources.money + 1000,
            ).model_dump()
        )


class TestManageResourcesOpenResourceAPI:
    endpoint = "user-progress/{user_id}/resource"

    @pytest.mark.parametrize(
        "resource_type",
        (
            ResourceType.KEYS,
            ResourceType.KEGS,
            ResourceType.BIG_KEGS,
            ResourceType.CHESTS,
        ),
    )
    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_open_resource_success(
        self,
        resource_type: ResourceType,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        user_resource_factory,
    ):
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        user_resources = await user_resource_factory(
            id=user_id,
            keys=1,
            chests=1,
            kegs=1,
            big_kegs=1,
        )

        response = await client.patch(
            self.endpoint.format(user_id=user_id),
            json={
                "subtype": ResourceActionSubtype.OPEN_BONUS_RESOURCE,
                "data": {
                    resource_type: -1,
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
                raw_bronze=0,
                raw_silver=0,
                raw_gold=0,
                bronze_ingots=0,
                silver_ingots=0,
                gold_ingots=0,
                crops=1000,
                wood=user_resources.wood,
                silk=0,
                kegs=1 if resource_type != ResourceType.KEGS else 0,
                big_kegs=1 if resource_type != ResourceType.BIG_KEGS else 0,
                chests=1 if resource_type != ResourceType.CHESTS else 0,
                keys=1 if resource_type != ResourceType.KEYS else 0,
                rare_gem=0,
                money=user_resources.money,
            ).model_dump()
        )

    @pytest.mark.parametrize("resource_type", (ResourceType.KEYS, ResourceType.KEGS))
    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_open_resource_insufficient_resource(
        self,
        resource_type: ResourceType,
        # service fixtures
        db_connection,
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        user_resource_factory,
    ):
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        await user_resource_factory(
            id=user_id,
            keys=0,
            kegs=0,
        )

        response = await client.patch(
            self.endpoint.format(user_id=user_id),
            json={
                "subtype": ResourceActionSubtype.OPEN_BONUS_RESOURCE,
                "data": {
                    resource_type: -1,
                },
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400

        # ресурсы реально не списались
        resources_left = await db_connection.fetchrow("""SELECT * FROM user_resources WHERE id = $1""", user_id)
        assert resources_left["keys"] == 0
        assert resources_left["kegs"] == 0

    @pytest.mark.parametrize("resource_type", (ResourceType.KEYS, ResourceType.KEGS))
    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_open_resource_cheat_with_positive_resource(
        self,
        resource_type: ResourceType,
        # service fixtures
        db_connection,
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        user_resource_factory,
    ):
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        await user_resource_factory(id=user_id)

        response = await client.patch(
            self.endpoint.format(user_id=user_id),
            json={
                "subtype": ResourceActionSubtype.OPEN_BONUS_RESOURCE,
                "data": {
                    resource_type: 3,  # вот тут должно быть отрицательное число, пытаемся хакнуть
                },
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400

        # ресурсы реально не изменились
        resources_left = await db_connection.fetchrow("""SELECT * FROM user_resources WHERE id = $1""", user_id)
        assert resources_left["keys"] == 3
        assert resources_left["kegs"] == 3


class TestManageResourcesTransitionAPI:
    endpoint = "user-progress/{user_id}/resource"

    @pytest.mark.parametrize(
        "action, resource, quantity, expected_result_money, expected_result_resource",
        (
            (ResourceTransitionActionType.BUY, ResourceType.WOOD, 1, 1600, 1100),
            (ResourceTransitionActionType.BUY, ResourceType.WOOD, 3, 800, 1300),
            (ResourceTransitionActionType.SELL, ResourceType.WOOD, 1, 2040, 900),
            (ResourceTransitionActionType.SELL, ResourceType.WOOD, 5, 2200, 500),
        ),
    )
    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_bonus_reward_buy_sell_success(
        self,
        action: ResourceTransitionActionType,
        resource: ResourceType,
        quantity,
        expected_result_money,
        expected_result_resource,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        user_resource_factory,
        user_upgrades_factory,
    ):
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        await user_upgrades_factory(id=user_id)

        user_resources = await user_resource_factory(id=user_id)

        response = await client.patch(
            self.endpoint.format(user_id=user_id),
            json={
                "subtype": ResourceActionSubtype.RESOURCE_TRANSITION,
                "data": {
                    "action": action,
                    "resource": resource,
                    "quantity": quantity,
                    # для buy, sell там всегда 1 элемент, поэтому так можно писать
                    "recipe": DEFAULT_RESOURCES_TRANSITIONS[resource][action][0],
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
                raw_bronze=0,
                raw_silver=0,
                raw_gold=0,
                bronze_ingots=0,
                silver_ingots=0,
                gold_ingots=0,
                crops=user_resources.crops,
                wood=expected_result_resource,  # вот тут собственно добавили ресурсы
                silk=0,
                kegs=user_resources.kegs,
                big_kegs=user_resources.big_kegs,
                chests=user_resources.chests,
                keys=user_resources.keys,
                rare_gem=0,
                money=expected_result_money,  # а тут списали деньги
            ).model_dump()
        )

    @pytest.mark.parametrize(
        "action, resource, quantity",
        (
            (ResourceTransitionActionType.BUY, ResourceType.SILK, 3),  # у нас 2000, 1 silk стоит 1000
            (ResourceTransitionActionType.SELL, ResourceType.GOLD_INGOTS, 1),  # у нас такого вообще нет
            (ResourceTransitionActionType.SELL, ResourceType.KEGS, 4),  # у нас есть только 3
        ),
    )
    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_bonus_reward_buy_sell_insufficient_resource(
        self,
        action: ResourceTransitionActionType,
        resource: ResourceType,
        quantity,
        # service fixtures
        db_connection,
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        user_resource_factory,
        user_upgrades_factory,
    ):
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        await user_upgrades_factory(id=user_id)
        await user_resource_factory(id=user_id)

        response = await client.patch(
            self.endpoint.format(user_id=user_id),
            json={
                "subtype": ResourceActionSubtype.RESOURCE_TRANSITION,
                "data": {
                    "action": action,
                    "resource": resource,
                    "quantity": quantity,
                    # для buy, sell там всегда 1 элемент, поэтому так можно писать
                    "recipe": DEFAULT_RESOURCES_TRANSITIONS[resource][action][0],
                },
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400

        # ресурсы реально не списались
        resources_left = await db_connection.fetchrow("""SELECT * FROM user_resources WHERE id = $1""", user_id)
        assert resources_left["money"] == 2000
        assert resources_left["gold_ingots"] == 0
        assert resources_left["kegs"] == 3

    @pytest.mark.parametrize(
        "action, resource",
        (
            (ResourceTransitionActionType.BUY, ResourceType.MONEY),  # деньги нельзя покупать сами по себе
            (ResourceTransitionActionType.SELL, ResourceType.MONEY),  # продавать тоже
            (ResourceTransitionActionType.BUY, ResourceType.KEYS),  # и ключи нельзя
            (ResourceTransitionActionType.SELL, ResourceType.KEYS),
            (ResourceTransitionActionType.BUY, ResourceType.RARE_GEM),  # и эти тоже нельзя
            (ResourceTransitionActionType.SELL, ResourceType.RARE_GEM),
        ),
    )
    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_bonus_reward_buy_sell_can_not(
        self,
        action: ResourceTransitionActionType,
        resource: ResourceType,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        user_resource_factory,
    ):
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        await user_resource_factory(id=user_id)

        response = await client.patch(
            self.endpoint.format(user_id=user_id),
            json={
                "subtype": ResourceActionSubtype.RESOURCE_TRANSITION,
                "data": {
                    "action": action,
                    "resource": resource,
                    "quantity": 1,
                    "recipe": {},
                },
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400

    @pytest.mark.parametrize(
        "quantity, expected_result_money, expected_raw_bronze_left",
        (
            (1, 1800, 201),  # оно стоит 50 raw_bronze и 200 денег, тут мы купили 1, осталось 201
            (5, 1000, 1),  # а тут мы купили 5, осталось всего 1 raw_bronze
        ),
    )
    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_bonus_reward_craft_bronze_ingots_success(
        self,
        quantity,
        expected_result_money,
        expected_raw_bronze_left,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        user_resource_factory,
        user_upgrades_factory,
    ):
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        user_upgrades = copy.deepcopy(DEFAULT_USER_UPGRADES)
        user_upgrades[UpgradeType.RESOURCES][UpgradeSubtype.INGOTS] = 1
        await user_upgrades_factory(id=user_id, data=user_upgrades)

        user_resources = await user_resource_factory(
            id=user_id,
            raw_bronze=251,  # потребуется для крафта бронзовых слитков
        )

        resource = ResourceType.BRONZE_INGOTS
        action = ResourceTransitionActionType.CRAFT

        response = await client.patch(
            self.endpoint.format(user_id=user_id),
            json={
                "subtype": ResourceActionSubtype.RESOURCE_TRANSITION,
                "data": {
                    "action": action,
                    "resource": resource,
                    "quantity": quantity,
                    # у него тоже только 1 элемент в списке
                    "recipe": DEFAULT_RESOURCES_TRANSITIONS[resource][action][0],
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
                raw_bronze=expected_raw_bronze_left,  # сколько-то его было, потратили на крафт
                raw_silver=0,
                raw_gold=0,
                bronze_ingots=quantity,  # а тут сколько заказали, столько и получили
                silver_ingots=0,
                gold_ingots=0,
                crops=user_resources.crops,
                wood=user_resources.wood,
                silk=0,
                kegs=user_resources.kegs,
                big_kegs=user_resources.big_kegs,
                chests=user_resources.chests,
                keys=user_resources.keys,
                rare_gem=0,
                money=expected_result_money,  # а тут списали деньги
            ).model_dump()
        )

    @pytest.mark.parametrize(
        "quantity, expected_result_money, expected_raw_gold_left, expected_scraps_left",
        (
            (1, 1000, 2, 1000),  # оно стоит 1000 scraps, 2 raw_gold и 1000 денег, тут мы купили 1
            (2, 0, 0, 0),  # а тут мы купили 2, и всего осталось по нулям
        ),
    )
    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_bonus_reward_craft_silk_success(
        self,
        quantity,
        expected_result_money,
        expected_raw_gold_left,
        expected_scraps_left,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        user_resource_factory,
        user_upgrades_factory,
    ):
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        user_upgrades = copy.deepcopy(DEFAULT_USER_UPGRADES)
        user_upgrades[UpgradeType.RESOURCES][UpgradeSubtype.SILK] = 1
        await user_upgrades_factory(id=user_id, data=user_upgrades)
        user_resources = await user_resource_factory(
            id=user_id,
            raw_gold=4,
            scraps=2000,
            money=2000,
        )

        response = await client.patch(
            self.endpoint.format(user_id=user_id),
            json={
                "subtype": ResourceActionSubtype.RESOURCE_TRANSITION,
                "data": {
                    "action": ResourceTransitionActionType.CRAFT,
                    "resource": ResourceType.SILK,
                    "quantity": quantity,
                    # у него тоже только 1 элемент в списке
                    "recipe": DEFAULT_RESOURCES_TRANSITIONS[ResourceType.SILK][ResourceTransitionActionType.CRAFT][0],
                },
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response_json = response.json()

        assert response.status_code == 200

        assert (
            response_json
            == UserResources(
                scraps=expected_scraps_left,
                raw_bronze=0,
                raw_silver=0,
                raw_gold=expected_raw_gold_left,  # сколько-то его было, потратили на крафт
                bronze_ingots=0,
                silver_ingots=0,
                gold_ingots=0,
                crops=user_resources.crops,
                wood=user_resources.wood,
                silk=quantity,  # а тут сколько заказали, столько и получили
                kegs=user_resources.kegs,
                big_kegs=user_resources.big_kegs,
                chests=user_resources.chests,
                keys=user_resources.keys,
                rare_gem=0,
                money=expected_result_money,  # а тут списали деньги
            ).model_dump()
        )

    @pytest.mark.parametrize(
        "quantity, expected_result_money, expected_raw_gold_left, expected_scraps_left",
        (
            (1, 2000, 1, 100),  # {SCRAPS: 100, RAW_GOLD: 1, MONEY: -1000},
            (3, 0, 3, 300),
        ),
    )
    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_bonus_reward_mill_silk_success(
        self,
        quantity,
        expected_result_money,
        expected_raw_gold_left,
        expected_scraps_left,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        user_resource_factory,
        user_upgrades_factory,
    ):
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        await user_upgrades_factory(id=user_id)

        user_resources = await user_resource_factory(
            id=user_id,
            silk=3,
            money=3000,
            scraps=0,
            raw_gold=0,
        )

        response = await client.patch(
            self.endpoint.format(user_id=user_id),
            json={
                "subtype": ResourceActionSubtype.RESOURCE_TRANSITION,
                "data": {
                    "action": ResourceTransitionActionType.MILL,
                    "resource": ResourceType.SILK,
                    "quantity": quantity,
                    # у него тоже только 1 элемент в списке
                    "recipe": DEFAULT_RESOURCES_TRANSITIONS[ResourceType.SILK][ResourceTransitionActionType.MILL][0],
                },
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response_json = response.json()

        assert response.status_code == 200

        assert (
            response_json
            == UserResources(
                scraps=expected_scraps_left,
                raw_bronze=0,
                raw_silver=0,
                raw_gold=expected_raw_gold_left,  # сколько-то его было, потратили на крафт
                bronze_ingots=0,
                silver_ingots=0,
                gold_ingots=0,
                crops=user_resources.crops,
                wood=user_resources.wood,
                silk=3 - quantity,  # а тут сколько заказали, столько и потратили
                kegs=user_resources.kegs,
                big_kegs=user_resources.big_kegs,
                chests=user_resources.chests,
                keys=user_resources.keys,
                rare_gem=0,
                money=expected_result_money,  # а тут списали деньги
            ).model_dump()
        )

    @pytest.mark.parametrize(
        "starting_scraps, starting_raw_gold, starting_money",
        (
            (500, 2, 1000),  # оно стоит 1000 scraps, 2 raw_gold и 1000 денег, тут не хватает scraps
            (1000, 1, 1000),  # оно стоит 1000 scraps, 2 raw_gold и 1000 денег, тут не хватает raw_gold
            (1000, 2, 500),  # оно стоит 1000 scraps, 2 raw_gold и 1000 денег, тут не хватает money
        ),
    )
    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_bonus_reward_craft_silk_insufficient_resources(
        self,
        starting_scraps,
        starting_raw_gold,
        starting_money,
        # service fixtures
        db_connection,
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        user_resource_factory,
        user_upgrades_factory,
    ):
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        await user_upgrades_factory(id=user_id)

        await user_resource_factory(
            id=user_id,
            raw_gold=starting_raw_gold,
            scraps=starting_scraps,
            money=starting_money,
        )

        response = await client.patch(
            self.endpoint.format(user_id=user_id),
            json={
                "subtype": ResourceActionSubtype.RESOURCE_TRANSITION,
                "data": {
                    "action": ResourceTransitionActionType.CRAFT,
                    "resource": ResourceType.SILK,
                    "quantity": 1,
                    # у него тоже только 1 элемент в списке
                    "recipe": DEFAULT_RESOURCES_TRANSITIONS[ResourceType.SILK][ResourceTransitionActionType.CRAFT][0],
                },
            },
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 400

        # ресурсы реально не списались
        resources_left = await db_connection.fetchrow("""SELECT * FROM user_resources WHERE id = $1""", user_id)
        assert resources_left["scraps"] == starting_scraps
        assert resources_left["raw_gold"] == starting_raw_gold
        assert resources_left["money"] == starting_money

    @pytest.mark.parametrize(
        (
            "quantity",
            "recipe_index",
            "expected_result_money",
            "expected_crops_left",
            "expected_wood_left",
            "expected_raw_bronze_left",
            "expected_bronze_ingots_left",
        ),
        (
            (1, 0, 2000, 200, 200, 300, 300),  # {CROPS: -100, WOOD: -100, MONEY: -1000}
            (3, 0, 0, 0, 0, 300, 300),
            (1, 1, 2000, 200, 300, 240, 300),  # {CROPS: -100, RAW_BRONZE: -60, MONEY: -1000}
            (3, 1, 0, 0, 300, 120, 300),
            (1, 2, 2000, 200, 300, 300, 290),  # {CROPS: -100, BRONZE_INGOTS: -10, MONEY: -1000}
            (3, 2, 0, 0, 300, 300, 270),
        ),
    )
    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_bonus_reward_craft_kegs_success(
        self,
        quantity,
        recipe_index,
        expected_result_money,
        expected_crops_left,
        expected_wood_left,
        expected_raw_bronze_left,
        expected_bronze_ingots_left,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        user_resource_factory,
        user_upgrades_factory,
    ):
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        user_upgrades = copy.deepcopy(DEFAULT_USER_UPGRADES)
        user_upgrades[UpgradeType.RESOURCES][UpgradeSubtype.KEGS] = 3
        await user_upgrades_factory(id=user_id, data=user_upgrades)

        user_resources = await user_resource_factory(
            id=user_id,
            crops=300,
            wood=300,
            raw_bronze=300,
            bronze_ingots=300,
            money=3000,
            kegs=0,  # изначально их было 0
        )

        action = ResourceTransitionActionType.CRAFT
        kegs = ResourceType.KEGS

        response = await client.patch(
            self.endpoint.format(user_id=user_id),
            json={
                "subtype": ResourceActionSubtype.RESOURCE_TRANSITION,
                "data": {
                    "action": action,
                    "resource": kegs,
                    "quantity": quantity,
                    # А ВОТ ТУТ мы берем разные рецепты для крафта!
                    "recipe": DEFAULT_RESOURCES_TRANSITIONS[kegs][action][recipe_index],
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
                raw_bronze=expected_raw_bronze_left,
                raw_silver=0,
                raw_gold=0,
                bronze_ingots=expected_bronze_ingots_left,
                silver_ingots=0,
                gold_ingots=0,
                crops=expected_crops_left,
                wood=expected_wood_left,
                silk=0,
                kegs=quantity,  # собственно вот тут мы его и получили
                big_kegs=user_resources.big_kegs,
                chests=user_resources.chests,
                keys=user_resources.keys,
                rare_gem=0,
                money=expected_result_money,  # а тут списали деньги
            ).model_dump()
        )
