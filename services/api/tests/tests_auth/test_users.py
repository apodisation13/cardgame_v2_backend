from datetime import UTC, datetime, timedelta
from unittest.mock import ANY

import pytest

from freezegun import freeze_time
from httpx import AsyncClient
from lib.utils.events.event_types import EventType
from services.api.app.apps.auth.lib import create_token, decode_token, get_password_hash
from services.api.app.apps.auth.schemas import TokenType, UserRegisterResponse
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

    @pytest.mark.usefixtures("init_db_cards")
    @pytest.mark.asyncio
    async def test_register_user_success(
        self,
        # service fixtures
        event_sender_mock,
        client: AsyncClient,
        db_connection,
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
        assert user_levels == 2

        user_seasons: int = await db_connection.fetchval("""SELECT COUNT(*) FROM user_seasons""")
        assert user_seasons == 1

        user_resources: list[dict] = await db_connection.fetch(
            """
            SELECT
                scraps,
                raw_bronze,
                raw_silver,
                raw_gold,
                bronze_ingots,
                silver_ingots,
                gold_ingots,
                crops,
                wood,
                silk,
                kegs,
                big_kegs,
                chests,
                keys,
                rare_gem,
                money
            FROM user_resources
            """,
        )
        assert len(user_resources) == 1

        assert (
            dict(user_resources[0])
            == UserResources(
                scraps=1000,
                raw_bronze=0,
                raw_silver=0,
                raw_gold=0,
                bronze_ingots=0,
                silver_ingots=0,
                gold_ingots=0,
                crops=1000,
                wood=1000,
                silk=0,
                kegs=0,
                big_kegs=0,
                chests=0,
                keys=1,
                rare_gem=0,
                money=3000,
            ).model_dump()
        )

        assert event_sender_mock.call_args.kwargs["event_type"] == EventType.USER_REGISTRATION
        assert event_sender_mock.call_args.kwargs["payload"] == {"user_id": 1}

    @pytest.mark.asyncio
    async def test_register_user_incorrect_data(
        self,
        # service fixtures
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
        # service fixtures
        client: AsyncClient,
        # fixtures for test
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
        # service fixtures
        client: AsyncClient,
        db_connection,
        # fixtures for test
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
                "refresh_token": ANY,
            },
        }

    @pytest.mark.asyncio
    async def test_user_login_incorrect_data(
        self,
        # service fixtures
        client: AsyncClient,
        db_connection,
        # fixtures for test
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

        assert response.status_code == 400
        assert response_json == {"error": {"code": "BAD_REQUEST", "details": "UserNotFoundError()", "message": ""}}

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
        # service fixtures
        client: AsyncClient,
        db_connection,
        # fixtures for test
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

        assert response.status_code == 400
        assert response_json == {"error": {"code": "BAD_REQUEST", "details": "UserNotFoundError()", "message": ""}}

    @pytest.mark.asyncio
    async def test_wrong_user_access(
        self,
        # service fixtures
        client: AsyncClient,
        db_connection,
        # fixtures for test
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

    @pytest.mark.asyncio
    async def test_user_login_empty_data(
        self,
        # service fixtures
        client: AsyncClient,
        db_connection,
        # fixtures for test
        user_factory,
    ) -> None:
        response = await client.post(
            self.endpoint,
            json={
                "email": "",
                "password": "",
            },
        )

        assert response.status_code == 422


class TestRefreshAccessTokenAPI:
    endpoint = "users/refresh-token"

    @pytest.mark.asyncio
    async def test_user_refresh_token_success(
        self,
        # service fixtures
        app_config,
        client: AsyncClient,
        db_connection,
        # fixtures for test
        user_factory,
    ) -> None:
        user = await user_factory(
            email="email@mail.ru",
            password=get_password_hash("password"),
            username="username",
        )

        token_data = {"sub": user.email.lower()}

        refresh_token = create_token(
            config=app_config,
            data=token_data,
            token_type=TokenType.REFRESH_TOKEN,
        )

        response = await client.post(
            self.endpoint,
            json={
                "refresh_token": refresh_token,
            },
        )

        response_json = response.json()
        assert response.status_code == 200

        assert response_json == {
            "access_token": ANY,
            "token_type": "bearer",
        }

        access_token = response_json["access_token"]

        email, token_type = decode_token(app_config, access_token)

        assert email == user.email
        assert token_type == TokenType.ACCESS_TOKEN

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "expires_in, expected_status",
        [
            (4, 200),
            (12, 401),
        ],
    )
    async def test_user_refresh_token_expired(
        self,
        expires_in,
        expected_status,
        # service fixtures
        app_config,
        client: AsyncClient,
        db_connection,
        # fixtures for test
        user_factory,
    ) -> None:
        app_config.ACCESS_TOKEN_EXPIRE_MINUTES = 1
        app_config.REFRESH_TOKEN_EXPIRE_MINUTES = 10

        user = await user_factory(
            email="email@mail.ru",
            password=get_password_hash("password"),
            username="username",
        )

        token_data = {"sub": user.email.lower()}

        # как будто юзер создал этот токен слишком давно
        time_past = datetime.now(UTC) - timedelta(minutes=expires_in)
        with freeze_time(time_past):
            refresh_token = create_token(
                config=app_config,
                data=token_data,
                token_type=TokenType.REFRESH_TOKEN,
            )

        response = await client.post(
            self.endpoint,
            json={
                "refresh_token": refresh_token,
            },
        )

        response_json = response.json()
        assert response.status_code == expected_status

        if expected_status == 401:
            assert response_json == {"detail": "Refresh token expired. Please login again."}
