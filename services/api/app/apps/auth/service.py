import logging

from asyncpg import UniqueViolationError

from fastapi import HTTPException, status
from lib.utils.db.pool import Database
from lib.utils.events import event_sender
from lib.utils.events.event_types import EventType
from services.api.app.apps.auth.lib import create_access_token, decode_token, get_password_hash, verify_password
from services.api.app.apps.auth.schemas import Token, User, UserLogin, UserRegister
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

    async def get_users(self) -> list[User]:
        print("STR28!!!!!!!!!!!!!!!!!!!!", self.config.AAA)
        async with self.db_pool.connection() as conn:
            result = await conn.fetch("""select id, username, email from users""")

        # accounts = [UsersList(id=row['id'], username=row['username'], email="s") for row in result]
        # return [UsersList(**dict(row)) for row in result]

        logger.info("RESULT!!!!!!!!!!!!!!!!!!!!! %s", result)

        await event_sender.create_event(
            event_type=EventType.EVENT_1,
            payload={"users": dict(result[0]) if result else []},
            config=self.config,
        )

        return [User.model_validate(dict(row)) for row in result]

    async def register_user(
        self,
        user_data: UserRegister,
    ) -> User:
        hashed_password: str = get_password_hash(user_data.password)

        async with self.db_pool.connection() as conn:
            try:
                user_id = await conn.fetchval(
                    """
                    INSERT INTO users
                    (username, email, password)
                    VALUES ($1, $2, $3)
                    RETURNING id
                    """,
                    user_data.username,
                    user_data.email,
                    hashed_password,
                )
            except UniqueViolationError as e:
                raise UserAlreadyExistsError(e) from e

        user_model = {
            "id": user_id,
            "username": user_data.username,
            "email": user_data.email,
        }
        return User.model_validate(user_model)

    async def login(
        self,
        user_data: UserLogin,
    ) -> Token:
        user: UserRegister = await self._get_authenticated_user(
            email=user_data.email,
            password=user_data.password,
        )

        access_token = create_access_token(
            data={"sub": user.email},
            # expires_delta_minutes=access_token_expires,
        )

        token = Token(access_token=access_token, token_type="bearer")
        return Token.model_validate(token)

    async def _get_user_from_db(
        self,
        email: str,
    ) -> UserRegister:
        async with self.db_pool.connection() as conn:
            user = await conn.fetchrow(
                """
                SELECT
                    username,
                    email,
                    password
                FROM
                    users
                WHERE
                    email = $1
                """,
                email,
            )
        if not user:
            raise UserNotFoundError()

        return UserRegister.model_validate(dict(user))

    async def _get_authenticated_user(
        self,
        email: str,
        password: str,
    ) -> UserRegister:
        user: UserRegister = await self._get_user_from_db(email=email)
        verify_password(password, user.password)
        return user

    async def get_current_user(
        self,
        token: str,
    ) -> UserRegister:
        email = decode_token(token)

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await self._get_user_from_db(email=email)
        return user
