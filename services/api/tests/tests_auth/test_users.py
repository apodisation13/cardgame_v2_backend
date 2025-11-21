import pytest
from httpx import AsyncClient


class TestUsersAPI:
    """Асинхронные тесты для эндпоинта /auth"""

    @pytest.mark.asyncio
    async def test_get_users_empty(
        self,
        client: AsyncClient,
        db_connection,
        event_sender_mock,
    ) -> None:
        a = await db_connection.fetch("SELECT * FROM users")
        print("STR20", a)


        response = await client.get("/users/list-users")

        assert response.status_code == 200
        assert response.json() == []

        print(event_sender_mock.call_args_list)
