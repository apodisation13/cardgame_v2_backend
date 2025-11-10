import os
from enum import StrEnum
from pathlib import Path

from dotenv import load_dotenv


# # Получаем путь к корню проекта (где лежит .env файл)
# project_root = Path(__file__).parent.parent.parent.parent
# env_path = project_root / '.env'
#
# print(f"Looking for .env at: {env_path}")  # Для отладки

# Загружаем .env из корня проекта
# load_dotenv(env_path)
load_dotenv()



class BaseConfig:
    """Все настройки через env переменные"""

    # Environment
    CONFIG: str = os.getenv("CONFIG")

    # Database
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME")

    DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    print("STR35", DB_URL)


class TestingConfig(BaseConfig):
    ...


class ProductionConfig(BaseConfig):
    ...


class DevelopmentLocalConfig(BaseConfig):
    ...


class TestsLocalConfig(BaseConfig):
    DEBUG: bool = True
    TESTING: bool = True


class EnvType(StrEnum):
    TESTING = "testing"
    PRODUCTION = "production"
    DEVELOPMENT_LOCAL = "development_local"
    TEST_LOCAL = "test_local"


CONFIG_MAP = {
    EnvType.TEST_LOCAL: TestsLocalConfig,
    EnvType.DEVELOPMENT_LOCAL: DevelopmentLocalConfig,
    EnvType.TESTING: TestingConfig,
    EnvType.PRODUCTION: ProductionConfig,
}


def get_config() -> BaseConfig:
    config_name: str = os.getenv("CONFIG", "development_local")
    print("STR59", config_name)

    if config_name not in CONFIG_MAP:
        raise ValueError(f"Unknown config: {config_name}")

    env_type: EnvType = EnvType(config_name)
    config_class = CONFIG_MAP[env_type]

    print("STR67", config_class)
    return config_class()


# # Глобальный инстанс настроек
# settings = get_config()
