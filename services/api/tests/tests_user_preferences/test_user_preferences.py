import pytest

from httpx import AsyncClient
from services.api.app.apps.preferences.schemas import DEFAULT_PREFERENCES


class TestUserPreferencesAPI:
    endpoint = "preferences/user-preferences/{user_id}"

    @pytest.mark.asyncio
    async def test_get_non_existing_preferences(
        self,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
    ):
        """
        Тут у юзера еще нет сохраненных настроек, и мы заинзертим ему новых (дефолтных)
        """
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        response = await client.get(
            self.endpoint.format(user_id=user_id),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response_json = response.json()
        assert response.status_code == 200
        assert response_json == {"data": DEFAULT_PREFERENCES}

    @pytest.mark.asyncio
    async def test_get_already_existing_preferences(
        self,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        user_preferences_factory,
    ):
        """
        А тут у юзера уже есть какие-то настройки, соответственно вернутся они
        """
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        preferences = DEFAULT_PREFERENCES.copy()
        preferences.update(
            {
                "sound_on": False,
                "move_timeout": 100,
            },
        )

        await user_preferences_factory(
            id=user_id,
            data=preferences,
        )

        response = await client.get(
            self.endpoint.format(user_id=user_id),
            headers={"Authorization": f"Bearer {access_token}"},
        )

        response_json = response.json()
        assert response.status_code == 200
        assert response_json == {"data": preferences}

    @pytest.mark.asyncio
    async def test_update_already_existing_preferences(
        self,
        # service fixtures
        client: AsyncClient,
        user_login_fixture,
        # fixtures for test
        user_preferences_factory,
    ):
        """
        А тут у юзера уже есть какие-то настройки, и приходит запрос на их изменение
        """
        user_id = user_login_fixture["id"]
        access_token = user_login_fixture["token"]["access_token"]

        await user_preferences_factory(
            id=user_id,
            data=DEFAULT_PREFERENCES,
        )

        # вот тут с фронта пока приходят всегда все настройки
        preferences_to_change = {
            "data": {
                "sound_on": False,
                "animation_on": True,
                "move_timeout": 100,
                "avatar": None,
                "theme": 1,
            },
        }

        response = await client.patch(
            self.endpoint.format(user_id=user_id),
            headers={"Authorization": f"Bearer {access_token}"},
            json=preferences_to_change,
        )

        response_json = response.json()
        assert response.status_code == 200
        assert response_json == preferences_to_change
