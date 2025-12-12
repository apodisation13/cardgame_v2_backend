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


def get_secret(
    secret_name: str,
    default: str | float | bool = None,
) -> str:
    return os.getenv(secret_name, default)


def load_env():
    if "CONFIG" in os.environ:
        return
    load_dotenv()
