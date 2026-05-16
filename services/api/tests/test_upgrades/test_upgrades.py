import copy
from unittest.mock import patch

import pytest
from httpx import AsyncClient

from lib.utils.schemas.game import DEFAULT_USER_UPGRADES, UpgradeType, UpgradeSubtype, DEFAULT_UPGRADES, ResourceType


class TestUserUpgradesAPI:
    endpoint = "user-upgrades/{user_id}"

    @pytest.mark.asyncio
    async def test_get_non_existing_upgrades(
        self,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
    ):
        """
        Тут у юзера еще нет сохраненных прокачек, и мы заинзертим ему новых (дефолтных)
        """
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        response = await client.get(
            self.endpoint.format(user_id=user_id),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response_json = response.json()
        assert response.status_code == 200
        assert response_json == DEFAULT_USER_UPGRADES

    @pytest.mark.asyncio
    async def test_get_already_existing_upgrades(
        self,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        user_upgrades_factory,
    ):
        """
        А тут у юзера уже есть какие-то прокачки, соответственно вернутся они
        """
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        upgrades = copy.deepcopy(DEFAULT_USER_UPGRADES)
        upgrades[UpgradeType.RESOURCES][UpgradeSubtype.MAX_CARDS_IN_DECK] = 1

        await user_upgrades_factory(
            id=user_id,
            data=upgrades,
        )

        response = await client.get(
            self.endpoint.format(user_id=user_id),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response_json = response.json()
        assert response.status_code == 200
        assert response_json == upgrades

    @pytest.mark.asyncio
    async def test_post_upgrade_success(
        self,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        game_constants_factory,
        user_upgrades_factory,
        user_resource_factory,
    ):
        """
        Прокачиваем склад денег с уровня 0 до уровня 1, потом до уровня 2
        А потом не можем прокачать, ресурсов не хватает
        """
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        upgrades_copy = copy.deepcopy(DEFAULT_USER_UPGRADES)

        await game_constants_factory()
        await user_upgrades_factory(
            id=user_id,
            data=upgrades_copy,
        )
        await user_resource_factory(
            id=user_id,
            money=3000,
            crops=1500,
            raw_bronze=80,
        )

        """
        Вот сколько нужно ресурсов на прокачку с уровня 0 на уровень 1:
        "next": {
            ResourceType.MONEY: -1000,
            ResourceType.CROPS: -500,
            ResourceType.RAW_BRONZE: -30,
        },
        
        А вот с уровня 1 на уровень 2:
        "next": {
            ResourceType.MONEY: -2000,
            ResourceType.CROPS: -1000,
            ResourceType.RAW_BRONZE: -50,
        },
        """

        response = await client.post(
            self.endpoint.format(user_id=user_id),
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "upgrade_type": UpgradeType.RESOURCES,
                "upgrade_subtype": UpgradeSubtype.MONEY,
            },
        )

        response_json = response.json()
        assert response.status_code == 200

        resources = response_json["resources"]
        upgrades = response_json["upgrades"]

        assert resources["money"] == 2000
        assert resources["crops"] == 1000
        assert resources["raw_bronze"] == 50

        # был уровень 0, стал уровень 1!
        assert upgrades[UpgradeType.RESOURCES][UpgradeSubtype.MONEY] == 1

        upgrades[UpgradeType.RESOURCES].pop(UpgradeSubtype.MONEY)
        upgrades_copy[UpgradeType.RESOURCES].pop(UpgradeSubtype.MONEY)

        # за исключением денег - остальные не изменились
        assert upgrades == upgrades_copy

        # повторный запрос - прокачиваем еще раз склад денег, и пока ресурсов всё ещё хватает
        response = await client.post(
            self.endpoint.format(user_id=user_id),
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "upgrade_type": UpgradeType.RESOURCES,
                "upgrade_subtype": UpgradeSubtype.MONEY,
            },
        )

        response_json = response.json()
        assert response.status_code == 200

        resources = response_json["resources"]
        upgrades = response_json["upgrades"]

        assert resources["money"] == 0
        assert resources["crops"] == 0
        assert resources["raw_bronze"] == 0

        # был уровень 1, стал уровень 2!
        assert upgrades[UpgradeType.RESOURCES][UpgradeSubtype.MONEY] == 2

        upgrades[UpgradeType.RESOURCES].pop(UpgradeSubtype.MONEY)

        # за исключением денег - остальные не изменились
        assert upgrades == upgrades_copy

    @pytest.mark.asyncio
    async def test_post_upgrade_insufficient_resources(
        self,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        game_constants_factory,
        user_upgrades_factory,
        user_resource_factory,
    ):
        """
        Прокачиваем склад денег с уровня 0 до уровня 1, но ресурсов не хватает
        """
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        upgrades_copy = copy.deepcopy(DEFAULT_USER_UPGRADES)

        await game_constants_factory()
        await user_upgrades_factory(
            id=user_id,
            data=upgrades_copy,
        )
        await user_resource_factory(
            id=user_id,
            money=500,  # вот этого не хватает
            crops=500,
            raw_bronze=100,
        )

        """
        Вот сколько нужно ресурсов на прокачку с уровня 0 на уровень 1:
        "next": {
            ResourceType.MONEY: -1000,
            ResourceType.CROPS: -500,
            ResourceType.RAW_BRONZE: -30,
        }
        """

        # вот тут ресурсов уже не хватает, кинется 400 ошибка
        response = await client.post(
            self.endpoint.format(user_id=user_id),
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "upgrade_type": UpgradeType.RESOURCES,
                "upgrade_subtype": UpgradeSubtype.MONEY,
            },
        )

        response_json = response.json()
        assert response.status_code == 400

        message = f"Scenario: Post upgrade: type {UpgradeType.RESOURCES}, subtype {UpgradeSubtype.MONEY}, user_id: {user_id}, resource: {ResourceType.MONEY} - insufficient resources (actual: {500-1000})"

        assert response_json == {
            'error': {
                'code': 'BAD_REQUEST',
                'message': message,
                'details': f"NegativeResourcesError('{message}')",
            },
        }

    @pytest.mark.asyncio
    async def test_post_upgrade_max_level_reached(
        self,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        game_constants_factory,
        user_upgrades_factory,
        user_resource_factory,
    ):
        """
        Прокачиваем склад денег с уровня 9 до уровня 10, а потом пытаемся прокачать еще раз
        """
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        upgrades_copy = copy.deepcopy(DEFAULT_USER_UPGRADES)
        upgrades_copy[UpgradeType.RESOURCES][UpgradeSubtype.MONEY] = 10  # уже 10й уровень, последний

        await game_constants_factory()
        await user_upgrades_factory(
            id=user_id,
            data=upgrades_copy,
        )
        await user_resource_factory(id=user_id)

        # уже достигнут максимальный уровень, дальше невозможно прокачать (с фронта тоже блокировка есть)
        response = await client.post(
            self.endpoint.format(user_id=user_id),
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "upgrade_type": UpgradeType.RESOURCES,
                "upgrade_subtype": UpgradeSubtype.MONEY,
            },
        )

        response_json = response.json()
        assert response.status_code == 400

        assert response_json == {
            'error': {
                'code': 'BAD_REQUEST',
                'message': 'User 1 already at max level for resources/money',
                'details': "UpgradeMaxLevelReachedError('User 1 already at max level for resources/money')",
            },
        }

    @pytest.mark.asyncio
    async def test_post_upgrade_new_upgrade_type(
        self,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        game_constants_factory,
        user_upgrades_factory,
        user_resource_factory,
    ):
        """
        Когда-то в будущем добавим в енамы новый элемент, и проверим что оно не сломалось
        Первый раз качаем что-то другое, а второй раз - сразу качаем новые
        """
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        # вот так было изначально у юзера - без нового поля
        old_user_upgrades = copy.deepcopy(DEFAULT_USER_UPGRADES)
        await user_upgrades_factory(
            id=user_id,
            data=old_user_upgrades,
        )

        # схема прокачек в константах - с новым полем
        new_upgrades_config = copy.deepcopy(DEFAULT_UPGRADES)
        new_upgrades_config[UpgradeType.SETTINGS]["upgrades"]["NEW_FIELD_ONE"] = {
            "ordering": 10,
            "title": "New Field One",
            "upgrades": {
                0: {
                    "value": False,
                    "next": {
                        ResourceType.MONEY: -10000,
                    },
                },
                1: {"value": True, "next": None},
            },
        }
        await game_constants_factory(
            data={"upgrades": new_upgrades_config},
        )

        # DEFAULT_USER_UPGRADES тоже обновился - теперь там есть новое поле
        new_user_defaults = copy.deepcopy(DEFAULT_USER_UPGRADES)
        new_user_defaults[UpgradeType.SETTINGS]["NEW_FIELD_ONE"] = 0

        await user_resource_factory(
            id=user_id,
            money=3000,
            crops=1500,
            raw_bronze=80,
        )

        """
        Вот сколько нужно ресурсов на прокачку с уровня 0 на уровень 1:
        "next": {
            ResourceType.MONEY: -1000,
            ResourceType.CROPS: -500,
            ResourceType.RAW_BRONZE: -30,
        }
        """

        # решили прокачать деньги - сервис увидит новое поле в DEFAULT_USER_UPGRADES
        # и автоматически добавит его юзеру при миграции
        with patch("services.api.app.apps.upgrades.service.DEFAULT_USER_UPGRADES", new_user_defaults):
            response = await client.post(
                self.endpoint.format(user_id=user_id),
                headers={"Authorization": f"Bearer {access_token}"},
                json={
                    "upgrade_type": UpgradeType.RESOURCES,
                    "upgrade_subtype": UpgradeSubtype.MONEY,
                },
            )

        response_json = response.json()
        assert response.status_code == 200

        resources = response_json["resources"]
        upgrades = response_json["upgrades"]

        assert resources["money"] == 2000
        assert resources["crops"] == 1000
        assert resources["raw_bronze"] == 50

        # был уровень 0, стал уровень 1
        assert upgrades[UpgradeType.RESOURCES][UpgradeSubtype.MONEY] == 1

        upgrades[UpgradeType.RESOURCES].pop(UpgradeSubtype.MONEY)
        new_user_defaults[UpgradeType.RESOURCES].pop(UpgradeSubtype.MONEY)

        # за исключением денег - остальные не изменились + добавилось NEW_FIELD_ONE!
        assert upgrades == new_user_defaults
