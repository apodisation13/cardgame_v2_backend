import pytest

from httpx import AsyncClient


class TestOpenRelatedLevelsAPI:
    endpoint = "user-progress/{user_id}/open-related-levels/{user_level_id}"

    @pytest.mark.parametrize("level_finished", [True, False])
    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_open_open_level_without_related_levels(
        self,
        level_finished: bool,
        client: AsyncClient,
        db_connection,
        level_factory,
        level_enemy_factory,
        user_login_fixture,
        user_level_factory,
        user_season_factory,
    ):
        """
        Базовая фикстура добавила уже 4 разных уровня
        У юзера открыт уровень id=5, который мы создали в этом тесте
        У этого уровня нет связанных уровней (level_related_levels)
        Соответственно если юзер проходит этот уровень, то ему мы поставим finished
        И всё, открывать новые не надо, их ведь нет
        Если уровень УЖЕ пройден, ничего страшного, так и останется
        """
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        level = await level_factory(
            season_id=1,
            enemy_leader_id=1,
        )
        # чтобы ручка корректно вернула, что этот уровень есть вообще, по коду стоит JOIN level_enemies
        await level_enemy_factory(
            level_id=level.id,
            enemy_id=1,
        )

        user_level = await user_level_factory(
            user_id=user_id,
            level_id=level.id,
            finished=level_finished,
        )
        await user_season_factory(
            user_id=user_id,
            season_id=1,
        )

        response = await client.patch(
            self.endpoint.format(user_id=user_id, user_level_id=user_level.id),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        response_json = response.json()

        # в 1м сезоне добавился 1 уровень!
        levels = response_json["seasons"][0]["season"]["levels"]
        assert len(levels) == 4  # 3 было по дефолту, и еще 1 мы в этом тесте создали
        # во 2м сезоне без изменения
        levels = response_json["seasons"][1]["season"]["levels"]
        assert len(levels) == 1

        user_levels: list[dict] = await db_connection.fetch("""SELECT * FROM user_levels""")
        assert len(user_levels) == 1
        assert user_levels[0]["finished"] is True  # вот это самое главное - уровню поставилось что он пройден

    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_open_open_level_with_related_levels(
        self,
        client: AsyncClient,
        db_connection,
        user_login_fixture,
        user_level_factory,
    ):
        """
        Базовая фикстура добавила уже 3 разных уровня, и там у уровня 1 есть связанные: 2 и 3
        Соответственно если юзер проходит этот уровень, то ему мы поставим finished
        А уровни 2 и 3 - станут unlocked для юзера
        Если исходный уровень УЖЕ пройден, ничего страшного, так и останется (2й запрос)
        """
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        # 1й уровень открыт у юзера, но еще не пройден
        user_level = await user_level_factory(
            user_id=user_id,
            level_id=1,
            finished=False,
        )

        user_levels: list[dict] = await db_connection.fetch("""SELECT * FROM user_levels""")
        assert len(user_levels) == 1
        assert user_levels[0]["finished"] is False

        response = await client.patch(
            self.endpoint.format(user_id=user_id, user_level_id=user_level.id),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        response_json = response.json()

        levels = response_json["seasons"][0]["season"]["levels"]
        assert len(levels) == 3  # 3 было по дефолту

        levels = response_json["seasons"][1]["season"]["levels"]
        assert len(levels) == 1  # для сезона 2 ничего не поменялось

        user_levels: list[dict] = await db_connection.fetch("""SELECT * FROM user_levels ORDER BY updated_at""")

        # а вот тут важно: был 1 уровень, он стал пройденным, а 2 новых открылись!
        assert len(user_levels) == 3

        assert user_levels[0]["finished"] is True  # вот это самое главное - 1му уровню поставилось что он пройден

        # а эти стали открыты, но не пройдены
        assert user_levels[1]["finished"] is False
        assert user_levels[2]["finished"] is False

        # --------------- повторный запрос на тот же уже пройденный уровень ---------------
        response = await client.patch(
            self.endpoint.format(user_id=user_id, user_level_id=user_level.id),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        response_json = response.json()

        levels = response_json["seasons"][0]["season"]["levels"]
        assert len(levels) == 3

        user_levels: list[dict] = await db_connection.fetch("""SELECT * FROM user_levels ORDER BY updated_at""")

        assert len(user_levels) == 3

        # он последним изменился, поэтому теперь он стал внизу)
        assert user_levels[2]["finished"] is True

        # ничего не изменилось!
        assert user_levels[1]["finished"] is False
        assert user_levels[0]["finished"] is False

        # --------------- а теперь проходит еще 2й уровень ---------------
        response = await client.patch(
            self.endpoint.format(user_id=user_id, user_level_id=2),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        response_json = response.json()

        levels = response_json["seasons"][0]["season"]["levels"]
        assert len(levels) == 3

        user_levels: list[dict] = await db_connection.fetch("""SELECT * FROM user_levels ORDER BY updated_at DESC""")

        assert len(user_levels) == 3

        # уровень 2 изменился самым первым, в списке последний
        assert user_levels[0]["id"] == 2
        assert user_levels[0]["finished"] is True

        # это 1й уровень, он как был, так и остался
        assert user_levels[1]["id"] == 1
        assert user_levels[1]["finished"] is True

        # ничего не изменилось с 3м уровнем! он все еще не пройден (но открыт, так как вообще есть в user_levels)
        assert user_levels[2]["id"] == 3
        assert user_levels[2]["finished"] is False

    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_open_open_level_related_levels_already_open(
        self,
        client: AsyncClient,
        db_connection,
        user_login_fixture,
        user_level_factory,
    ):
        """
        Базовая фикстура добавила уже 3 разных уровня, и там у уровня 1 есть связанные: 2 и 3
        Пусть у юзера уже открыты уровни 1 и 3 (и не важно, пройдены ли), он проходит 1, открывается только 2
        """
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        # 1й уровень открыт у юзера, но еще не пройден
        user_level = await user_level_factory(
            user_id=user_id,
            level_id=1,
            finished=False,
        )
        # 3й уровень открыт у юзера, и не важно, пройден он или нет
        await user_level_factory(
            user_id=user_id,
            level_id=3,
            finished=True,
        )

        # проходит 1й уровень
        response = await client.patch(
            self.endpoint.format(user_id=user_id, user_level_id=user_level.id),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200

        response_json = response.json()

        levels = response_json["seasons"][0]["season"]["levels"]
        assert len(levels) == 3  # 3 было по дефолту

        levels = response_json["seasons"][1]["season"]["levels"]
        assert len(levels) == 1  # для сезона 2 ничего не поменялось

        # поскольку там транзакция, то по updated_at не совсем корректно смотреть
        user_levels: list[dict] = await db_connection.fetch("""SELECT * FROM user_levels ORDER BY created_at DESC""")
        assert len(user_levels) == 3  # было 2, стало 3

        assert user_levels[0]["level_id"] == 2
        assert user_levels[0]["finished"] is False  # а вот это 2й - который открылся последним по времени

        assert user_levels[1]["level_id"] == 3
        assert user_levels[1]["finished"] is True  # это 3й уровень, который не изменился

        assert user_levels[2]["finished"] is True  # 1му уровню поставилось что он пройден
