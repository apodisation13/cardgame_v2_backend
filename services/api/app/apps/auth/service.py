import logging

from asyncpg import UniqueViolationError

from fastapi import HTTPException, status
from lib.utils.db.pool import Database
from lib.utils.schemas.users import UserRole
from services.api.app.apps.auth.lib import create_token, decode_token, get_password_hash, verify_password
from services.api.app.apps.auth.schemas import (
    RefreshTokenRequest,
    RefreshTokenResponse,
    Token,
    TokenType,
    UserCheckTokenResponse,
    UserLoginRequest,
    UserLoginResponse,
    UserRegisterRequest,
    UserRegisterResponse,
)
from services.api.app.apps.progress import logic
from services.api.app.config import Config
from services.api.app.exceptions import UserAlreadyExistsError, UserNotFoundError


logger = logging.getLogger(__name__)


class AuthService:
    def __init__(
        self,
        db_pool: Database,
        config: Config,
    ):
        self.db_pool = db_pool
        self.config = config

    # async def get_users(self) -> list[User]:
    #     print("STR28!!!!!!!!!!!!!!!!!!!!", self.config.AAA)
    #     async with self.db_pool.connection() as conn:
    #         result = await conn.fetch("""select id, username, email, image from users""")
    #
    #     # accounts = [UsersList(id=row['id'], username=row['username'], email="s") for row in result]
    #     # return [UsersList(**dict(row)) for row in result]
    #
    #     logger.info("RESULT!!!!!!!!!!!!!!!!!!!!! %s", result)
    #
    #     await event_sender.create_event(
    #         event_type=EventType.EVENT_1,
    #         payload={"users": dict(result[0]) if result else []},
    #         config=self.config,
    #     )
    #
    #     user_dict = [
    #         User.model_validate(
    #             {
    #                 "id": row["id"],
    #                 "username": row["username"],
    #                 "email": row["email"],
    #                 "image": f"media/{row['image']}" if row["image"] else None,
    #             }
    #         )
    #         for row in result
    #     ]
    #
    #     return user_dict

    async def register_user(
        self,
        user_data: UserRegisterRequest,
    ) -> UserRegisterResponse:
        email_to_lower = str(user_data.email).lower()
        logger.info("Registering user with email %s, username %s", email_to_lower, user_data.username)
        async with self.db_pool.transaction() as connection:
            try:
                user_id = await connection.fetchval(
                    """
                    INSERT INTO users
                    (email, username, password)
                    VALUES ($1, $2, $3)
                    RETURNING id
                    """,
                    email_to_lower,
                    user_data.username,
                    get_password_hash(user_data.password),
                )
            except UniqueViolationError as e:
                raise UserAlreadyExistsError(e) from e

            await logic.open_default_content(
                connection=connection,
                user_id=user_id,
            )

        user_model = {
            "id": user_id,
            "username": user_data.username,
            "email": email_to_lower,
        }
        logger.info("Successfully registered user %s", user_id)
        return UserRegisterResponse.model_validate(user_model)

    async def login_user(
        self,
        user_data: UserLoginRequest,
    ) -> UserLoginResponse:
        email_to_lower = str(user_data.email).lower()
        logger.info("Login user %s", email_to_lower)
        user: dict = await self._get_authenticated_user(
            email=email_to_lower,
            password=user_data.password,
        )

        token_data = {"sub": email_to_lower}

        access_token = create_token(
            config=self.config,
            data=token_data,
            token_type=TokenType.ACCESS_TOKEN,
        )
        refresh_token = create_token(
            config=self.config,
            data=token_data,
            token_type=TokenType.REFRESH_TOKEN,
        )

        token = Token(
            access_token=access_token,
            refresh_token=refresh_token,
        )

        # await event_sender.create_event(
        #     event_type=EventType.USER_REGISTRATION,
        #     payload={"user_id": user["id"]},
        #     config=self.config,
        # )

        return UserLoginResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            token=token,
        )

    async def _get_user_by_email(
        self,
        email: str,
    ) -> dict:
        async with self.db_pool.connection() as conn:
            user = await conn.fetchrow(
                """
                SELECT
                    id,
                    username,
                    is_active,
                    email_verified,
                    password,
                    email
                FROM
                    users
                WHERE
                    email = $1
                """,
                email,
            )
        if not user or not user["is_active"]:
            raise UserNotFoundError()

        return dict(user)

    async def _get_authenticated_user(
        self,
        email: str,
        password: str,
    ) -> dict:
        user: dict = await self._get_user_by_email(email=email)
        verify_password(password, user["password"])
        return user

    async def get_developer_user(
        self,
        email: str,
    ) -> None:
        async with self.db_pool.connection() as conn:
            username: str = await conn.fetchval(
                """
                SELECT
                    username
                FROM
                    users
                WHERE
                    email = $1
                    AND is_active IS TRUE
                    AND role = $2
                """,
                email,
                UserRole.DEVELOPER,
            )

        if not username:
            raise UserNotFoundError()

    async def get_user_by_token(
        self,
        token: str,
    ) -> UserCheckTokenResponse:
        result: tuple | None = decode_token(
            config=self.config,
            token=token,
        )

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        email = result[0]
        user = await self._get_user_by_email(email=email)

        return UserCheckTokenResponse(
            id=user["id"],
            email=user["email"],
        )

    async def refresh_access_token(
        self,
        user_data: RefreshTokenRequest,
    ) -> RefreshTokenResponse:
        result: tuple | None = decode_token(
            config=self.config,
            token=user_data.refresh_token,
        )

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired. Please login again.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        email, token_type = result[0], result[1]

        if token_type != TokenType.REFRESH_TOKEN:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )

        new_access_token = create_token(
            config=self.config,
            data={"sub": email.lower()},
            token_type=TokenType.ACCESS_TOKEN,
        )

        return RefreshTokenResponse(access_token=new_access_token)
