import logging

from asyncpg import UniqueViolationError

from fastapi import HTTPException, status
from lib.utils.db.pool import Database
from lib.utils.schemas.users import UserRole
from services.api.app.apps.auth.lib import create_access_token, decode_token, get_password_hash, verify_password
from services.api.app.apps.auth.schemas import (
    Token,
    UserLoginRequest,
    UserLoginResponse,
    UserRegisterRequest,
    UserRegisterResponse,
    UserCheckTokenResponse,
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
        async with self.db_pool.transaction() as connection:
            try:
                user_id = await connection.fetchval(
                    """
                    INSERT INTO users
                    (email, username, password)
                    VALUES ($1, $2, $3)
                    RETURNING id
                    """,
                    user_data.email,
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
            "email": user_data.email,
        }
        return UserRegisterResponse.model_validate(user_model)

    async def login_user(
        self,
        user_data: UserLoginRequest,
    ) -> UserLoginResponse:
        user: dict = await self._get_authenticated_user(
            email=str(user_data.email),
            password=user_data.password,
        )

        access_token = create_access_token(
            data={"sub": user_data.email},
            # expires_delta_minutes=1,
        )

        token = Token(access_token=access_token, token_type="bearer")
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

    async def get_current_user(
        self,
        token: str,
    ) -> UserRegisterRequest:
        email = decode_token(token)

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await self._get_user_by_email(email=email)

        return UserRegisterRequest(
            username=user["username"],
            email=user["email"],
            password=user["password"],
        )

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
        email = decode_token(token)

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await self._get_user_by_email(email=email)

        return UserCheckTokenResponse(
            id=user["id"],
            email=user["email"],
        )
