from enum import StrEnum
import os

from dotenv import load_dotenv


class EnvType(StrEnum):
    TESTING = "testing"
    PRODUCTION = "production"
    DEVELOPMENT_LOCAL = "development_local"
    TEST_LOCAL = "test_local"
    DOCKER_LOCAL = "docker_local"

    @classmethod
    def need_elastic(cls) -> list:
        return [
            cls.TESTING,
            cls.PRODUCTION,
            cls.DOCKER_LOCAL,
        ]

    @classmethod
    def docker_development(cls) -> list:
        return [
            cls.TESTING,
            cls.PRODUCTION,
            cls.DOCKER_LOCAL,
        ]


def get_secret(
    secret_name: str,
    default: str | float | bool = None,
    cast: type = str,
) -> str | int | float | bool:
    value = os.getenv(secret_name)

    if value is None or value == "":
        return default

    try:
        if cast is bool:
            if value.lower() == "true":
                return True
            elif value.lower() == "false":
                return False
            else:
                raise ValueError(f"Cannot convert '{value}' to bool")
        elif cast is int:
            return int(value)
        elif cast is float:
            return float(value)
        elif cast is str:
            return value
        else:
            raise ValueError(f"Unsupported type: {cast}")
    except (ValueError, TypeError) as e:
        if default is not None:
            return default
        raise ValueError(f"Failed to convert secret '{secret_name}' to {cast}: {e}") from e


def load_env():
    if "CONFIG" in os.environ:
        return
    load_dotenv()
