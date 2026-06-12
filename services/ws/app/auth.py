import logging

from jose import ExpiredSignatureError, JWTError, jwt
from lib.utils.db.pool import Database
from services.ws.app.config import Config


logger = logging.getLogger(__name__)


async def get_user_id_from_token(token: str, config: Config, db: Database) -> int | None:
    """
    Декодирует JWT токен, достаёт email, ищет user_id в БД.
    Возвращает None если токен невалидный или пользователь не найден.
    """
    try:
        payload = jwt.decode(
            token,
            config.USER_PASSWORD_SECRET_KEY,
            algorithms=[config.ALGORITHM],
            options={"verify_exp": True},
        )
        email: str = payload.get("sub")
        if not email:
            return None
    except (JWTError, ExpiredSignatureError):
        logger.warning("Invalid or expired token")
        return None

    async with db.connection() as conn:
        user_id = await conn.fetchval(
            "SELECT id FROM users WHERE email = $1 AND is_active = TRUE",
            email,
        )

    return user_id
