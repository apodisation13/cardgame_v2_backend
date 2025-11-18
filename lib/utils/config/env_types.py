from enum import StrEnum
import os

from dotenv import load_dotenv


if "CONFIG" not in os.environ:
    load_dotenv()


class EnvType(StrEnum):
    TESTING = "testing"
    PRODUCTION = "production"
    DEVELOPMENT_LOCAL = "development_local"
    TEST_LOCAL = "test_local"


def get_secret(
    secret_name: str,
    default: str | float | bool = None,
):
    if default is not None:
        return default
    return os.getenv(secret_name)
