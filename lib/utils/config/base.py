import os
import sys

from dotenv import load_dotenv
from lib.utils.config.env_types import EnvType, get_secret


if "CONFIG" not in os.environ:
    load_dotenv()


class BaseConfig:
    ENV_TYPE: EnvType = EnvType.DEVELOPMENT_LOCAL

    DEBUG: bool = get_secret("DEBUG", default=False)
    TESTING: bool = get_secret("DEBUG", default=False)

    # Environment
    CONFIG: str = get_secret("CONFIG")

    # Database
    DB_USER: str = get_secret("DB_USER")
    DB_PASSWORD: str = get_secret("DB_PASSWORD")
    DB_HOST: str = get_secret("DB_USER", default="localhost")
    DB_PORT: int = int(get_secret("DB_PORT", default=5432))
    DB_NAME: str = get_secret("DB_NAME")
    DB_URL: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Logging
    LOGGING_LEVEL = get_secret("LOGGING_LEVEL", default="INFO")
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s | %(name)s:%(lineno)d | %(levelname)s | %(message)s",
                "datefmt": "%H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "level": "DEBUG",
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": LOGGING_LEVEL,
            },
        },
    }

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS = get_secret('KAFKA_BOOTSTRAP_SERVERS', default='localhost:9092')
    KAFKA_TOPIC = get_secret('KAFKA_TOPIC', default='events')


class BaseTestingConfig(BaseConfig):
    ENV_TYPE: EnvType = EnvType.TESTING


class BaseProductionConfig(BaseConfig):
    ENV_TYPE: EnvType = EnvType.PRODUCTION


class BaseDevelopmentLocalConfig(BaseConfig):
    ENV_TYPE: EnvType = EnvType.DEVELOPMENT_LOCAL


class BaseTestLocalConfig(BaseConfig):
    load_dotenv()

    ENV_TYPE: EnvType = EnvType.TEST_LOCAL

    DB_USER: str = get_secret("TEST_DB_USER", default="postgres")
    DB_PASSWORD: str = get_secret("TEST_DB_PASSWORD")
    DB_HOST: str = get_secret("TEST_DB_HOST", default="localhost")
    DB_PORT: int = int(get_secret("TEST_DB_HOST", default=5432))
    DB_NAME: str = get_secret("TEST_DB_NAME", default="test_db")
    DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    DEBUG: bool = True
    TESTING: bool = True


CONFIG_MAP = {
    EnvType.TEST_LOCAL: BaseTestLocalConfig,
    EnvType.DEVELOPMENT_LOCAL: BaseDevelopmentLocalConfig,
    EnvType.TESTING: BaseTestingConfig,
    EnvType.PRODUCTION: BaseProductionConfig,
}


def get_config() -> BaseConfig:
    config_name: str = get_secret("CONFIG")

    if config_name not in CONFIG_MAP:
        raise ValueError(f"Unknown config: {config_name}")

    env_type: EnvType = EnvType(config_name)
    config_class = CONFIG_MAP[env_type]

    return config_class()


# Глобальный инстанс настроек
config: BaseConfig = get_config()
