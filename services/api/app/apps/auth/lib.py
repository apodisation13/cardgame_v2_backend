from datetime import UTC, datetime, timedelta
import hashlib
import secrets

from jose import ExpiredSignatureError, JWTError, jwt
from services.api.app.apps.auth.schemas import TokenType
from services.api.app.config import Config
from services.api.app.exceptions import UserIncorrectPasswordError


def get_password_hash(
    password: str,
) -> str:
    salt = secrets.token_hex(16)
    hash_obj = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    )
    return f"{salt}${hash_obj.hex()}"


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> None:
    salt, stored_hash = hashed_password.split("$")
    hash_obj = hashlib.pbkdf2_hmac(
        "sha256",
        plain_password.encode("utf-8"),
        salt.encode("utf-8"),
        100000,
    )
    computed_hash = hash_obj.hex()
    res = secrets.compare_digest(computed_hash, stored_hash)
    if not res:
        raise UserIncorrectPasswordError


def create_token(
    config: Config,
    data: dict,
    token_type: TokenType,
) -> str:
    # Создает токен: или access_token, или refresh_token в зависимости от token_type
    now = datetime.now(UTC)

    if token_type == TokenType.ACCESS_TOKEN:
        expire_minutes = config.ACCESS_TOKEN_EXPIRE_MINUTES
    elif token_type == TokenType.REFRESH_TOKEN:
        expire_minutes = config.REFRESH_TOKEN_EXPIRE_MINUTES
    else:
        raise Exception("Invalid token type")

    expire = now + timedelta(minutes=expire_minutes)
    to_encode = data.copy()
    to_encode.update(
        {
            "exp": expire,
            "type": token_type,
        },
    )
    encoded_jwt = jwt.encode(
        to_encode,
        config.USER_PASSWORD_SECRET_KEY,
        algorithm=config.ALGORITHM,
    )
    return encoded_jwt


def decode_token(
    config: Config,
    token: str,
) -> tuple[str, TokenType] | None:
    try:
        payload = jwt.decode(
            token,
            config.USER_PASSWORD_SECRET_KEY,
            algorithms=[config.ALGORITHM],
            options={"verify_exp": True},
        )

        email: str = payload.get("sub")

        if email is None:
            return None

        token_type: TokenType = payload.get("type")
        if token_type is None:
            return None

        return email, token_type

    except ExpiredSignatureError:
        return None
    except JWTError:
        return None
