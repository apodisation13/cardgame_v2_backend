from unittest.mock import ANY

import pytest

from httpx import AsyncClient
from services.api.app.apps.auth.lib import get_password_hash
from services.api.app.apps.auth.schemas import UserRegisterResponse
from services.api.app.apps.progress.schemas import UserResources


class TestUserRegisterAPI:
    endpoint = "users/register-user"

    # @pytest.mark.asyncio
    # async def test_get_users_empty_1(
    #     self,
    #     client: AsyncClient,
    #     db_connection,
    #     event_sender_mock,
    # ) -> None:
    #     a = await db_connection.fetch("SELECT * FROM users")
    #     print("STR20", a)
    #
    #     response = await client.get("/users/list-users")
    #
    #     assert response.status_code == 200
    #     assert response.json() == []
    #
    #     print(event_sender_mock.call_args_list)

    @pytest.mark.asyncio
    async def test_register_user_success(
        self,
        client: AsyncClient,
        db_connection,
        init_db_cards,
    ):
        users_before: list = await db_connection.fetch("""SELECT * FROM users""")
        assert len(users_before) == 0

        response = await client.post(
            self.endpoint,
            json={
                "email": "teSTemail@mail.ru",  # <- почта будет приведена к нижнему регистру на бэке тоже (и на фронте)
                "password": "password",
                "username": "username",
            },
        )

        response_json = response.json()

        assert response.status_code == 200
        assert (
            response_json
            == UserRegisterResponse(
                id=1,
                username="username",
                email="testemail@mail.ru",
            ).model_dump()
        )

        users_after: int = await db_connection.fetchval("""SELECT COUNT(*) FROM users""")
        assert users_after == 1

        user_cards: int = await db_connection.fetchval("""SELECT COUNT(*) FROM user_cards""")
        assert user_cards == 2

        user_leaders: int = await db_connection.fetchval("""SELECT COUNT(*) FROM user_leaders""")
        assert user_leaders == 1

        user_decks: int = await db_connection.fetchval("""SELECT COUNT(*) FROM user_decks""")
        assert user_decks == 1

        user_levels: int = await db_connection.fetchval("""SELECT COUNT(*) FROM user_levels""")
        assert user_levels == 1

        user_resources: list[dict] = await db_connection.fetch(
            """SELECT scraps, wood, kegs, big_kegs, chests, keys FROM user_resources""",
        )
        assert len(user_resources) == 1

        assert (
            dict(user_resources[0])
            == UserResources(
                scraps=1000,
                wood=1000,
                kegs=3,
                big_kegs=1,
                chests=0,
                keys=3,
            ).model_dump()
        )

    @pytest.mark.asyncio
    async def test_register_user_incorrect_data(
        self,
        client: AsyncClient,
    ):
        response = await client.post(
            self.endpoint,
            json={
                "email": "email@mail.ru",
                "password": "password",
                # <- вот тут не хватает username
            },
        )

        response_json = response.json()

        assert response.status_code == 422
        assert response_json == {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Поле 'Username' обязательно для заполнения",
                "details": {
                    "validation_errors": [
                        {
                            "field": "username",
                            "message": "Поле 'Username' обязательно для заполнения",
                            "type": "missing",
                            "original_message": "Field required",
                        },
                    ],
                },
            },
        }

        response = await client.post(
            self.endpoint,
            json={
                "email": "email@mail.ru",
                "password": "password",
                "username": "username",
                "fake": 1,  # <- вот это лишний параметр тут
            },
        )

        response_json = response.json()
        assert response.status_code == 422

        assert response_json == {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Ошибка в поле 'Fake': Extra inputs are not permitted",
                "details": {
                    "validation_errors": [
                        {
                            "field": "fake",
                            "message": "Ошибка в поле 'Fake': Extra inputs are not permitted",
                            "type": "extra_forbidden",
                            "original_message": "Extra inputs are not permitted",
                        },
                    ],
                },
            },
        }

        response = await client.post(
            self.endpoint,
            json={
                "email": "emailmail.ru",  # <- здесь нет значка собачки
                "password": "3",  # <- здесь пароль слишком короткий
                "username": "username",
            },
        )

        response_json = response.json()
        assert response.status_code == 422

        assert response_json == {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Ошибки валидации в полях: email, password",
                "details": {
                    "validation_errors": [
                        {
                            "field": "email",
                            "message": "Поле 'Email' должно содержать корректный email адрес",
                            "type": "value_error",
                            "original_message": "value is not a valid email address: "
                            "An email address must have an @-sign.",
                        },
                        {
                            "field": "password",
                            "message": "Ошибка в поле 'Password': String should have at least 5 characters",
                            "type": "string_too_short",
                            "original_message": "String should have at least 5 characters",
                        },
                    ],
                },
            },
        }

    @pytest.mark.asyncio
    async def test_register_user_already_exists(
        self,
        client: AsyncClient,
        user_factory,
    ):
        await user_factory(
            username="username",
            email="email@mail.ru",
        )

        response = await client.post(
            self.endpoint,
            json={
                "email": "email@mail.ru",
                "password": "password",
                "username": "username2",
            },
        )

        response_json = response.json()

        assert response.status_code == 400
        assert response_json == {
            "error": {
                "code": "BAD_REQUEST",
                "message": "Field {email} already exists",
                "details": "UserAlreadyExistsError(UniqueViolationError('"
                'duplicate key value violates unique constraint "ix_users_email"\'))',
            },
        }


class TestUserLoginAPI:
    endpoint = "users/login-user"

    @pytest.mark.asyncio
    async def test_user_login_success(
        self,
        client: AsyncClient,
        db_connection,
        user_factory,
    ) -> None:
        user = await user_factory(
            email="email@mail.ru",
            password=get_password_hash("password"),
            username="username",
        )

        response = await client.post(
            self.endpoint,
            json={
                "email": "emaIL@mail.ru",  # <- автоматически приводится тоже к нижнему регистру
                "password": "password",
            },
        )

        response_json = response.json()

        assert response.status_code == 200
        assert response_json == {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "token": {
                "token_type": "bearer",
                "access_token": ANY,
            },
        }

    @pytest.mark.asyncio
    async def test_user_login_incorrect_data(
        self,
        client: AsyncClient,
        db_connection,
        user_factory,
    ) -> None:
        await user_factory(
            email="email@mail.ru",
            password=get_password_hash("password"),
            username="username",
        )

        response = await client.post(
            self.endpoint,
            json={
                "email": "email@mail.ru",
                # <- не прислал тут пароль
            },
        )

        response_json = response.json()

        assert response.status_code == 422
        assert response_json == {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Поле 'Password' обязательно для заполнения",
                "details": {
                    "validation_errors": [
                        {
                            "field": "password",
                            "message": "Поле 'Password' обязательно для заполнения",
                            "type": "missing",
                            "original_message": "Field required",
                        },
                    ],
                },
            },
        }

        response = await client.post(
            self.endpoint,
            json={
                "email": "email2@mail.ru",  # <- неверный емейл, такого пользователя нет в базе
                "password": "password",
            },
        )

        response_json = response.json()

        assert response.status_code == 500
        assert response_json == {
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "UserNotFoundError",
                "details": "UserNotFoundError()",
            },
        }

        response = await client.post(
            self.endpoint,
            json={
                "email": "email@mail.ru",
                "password": "password2",  # <- неверный пароль
            },
        )

        response_json = response.json()

        assert response.status_code == 500
        assert response_json == {
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "UserIncorrectPasswordError",
                "details": "UserIncorrectPasswordError()",
            },
        }

    @pytest.mark.asyncio
    async def test_user_inactive_login(
        self,
        client: AsyncClient,
        db_connection,
        user_factory,
    ) -> None:
        await user_factory(
            email="email@mail.ru",
            password=get_password_hash("password"),
            username="username",
            is_active=False,
        )

        response = await client.post(
            self.endpoint,
            json={
                "email": "email@mail.ru",
                "password": "password",
            },
        )

        response_json = response.json()

        assert response.status_code == 500
        assert response_json == {
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "UserNotFoundError",
                "details": "UserNotFoundError()",
            },
        }

    @pytest.mark.asyncio
    async def test_wrong_user_access(
        self,
        client: AsyncClient,
        db_connection,
        user_factory,
    ) -> None:
        user_1 = await user_factory(
            email="email@mail.ru",
            password=get_password_hash("password"),
            username="username",
        )

        response = await client.post(
            self.endpoint,
            json={
                "email": user_1.email,
                "password": "password",
            },
        )

        response_json = response.json()

        assert response.status_code == 200
        user1_access_token = response_json["token"]["access_token"]

        # роут для данных от юзера users.id = 2
        token_protected_url = "/user-progress/2"

        # кто-то пытается постучаться по роуту, который закрыт авторизацией через токен
        response = await client.get(
            token_protected_url,
        )

        response_json = response.json()

        assert response.status_code == 401
        assert response_json == {"detail": "Missing authorization header"}

        # а теперь присылает совсем неверный токен
        response = await client.get(
            token_protected_url,
            headers={"Authorization": f"FFFBearer {user1_access_token}"},  # <- вот тут ошибка
        )

        response_json = response.json()

        assert response.status_code == 401
        assert response_json == {"detail": "Invalid authorization format. Use 'Bearer <token>'"}

        # а теперь как будто юзер пытается взять данные от чужого юзера
        response = await client.get(
            token_protected_url,
            headers={"Authorization": f"Bearer {user1_access_token}"},
        )

        response_json = response.json()

        assert response.status_code == 401
        assert response_json == {"detail": "Access denied"}
