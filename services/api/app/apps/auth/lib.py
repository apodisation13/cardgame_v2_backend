from datetime import UTC, datetime, timedelta

from jose import ExpiredSignatureError, JWTError, jwt
from services.api.app.exceptions import ErrorUserIncorrectPassword


SECRET_KEY = "your-secret-key-here"  # В продакшене используйте надежный ключ
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


import hashlib
import secrets


def get_password_hash(
    password: str,
) -> str:
    salt = secrets.token_hex(16)
    hash_obj = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000,
    )
    return f"{salt}${hash_obj.hex()}"


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> None:
    salt, stored_hash = hashed_password.split('$')
    hash_obj = hashlib.pbkdf2_hmac(
        'sha256',
        plain_password.encode('utf-8'),
        salt.encode('utf-8'),
        100000,
    )
    computed_hash = hash_obj.hex()
    res = secrets.compare_digest(computed_hash, stored_hash)
    if not res:
        raise ErrorUserIncorrectPassword


def create_access_token(
    data: dict,
    expires_delta_minutes: int = 30,
):
    now = datetime.now(UTC)
    expire = now + timedelta(minutes=expires_delta_minutes)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"verify_exp": True},
        )

        email: str = payload.get("sub")

        if email is None:
            return None
        return email

    except ExpiredSignatureError:
        return None
    except JWTError:
        return None
