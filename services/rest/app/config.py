import sys
import os

from dotenv import load_dotenv


# Добавляем apps в путь Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

from lib.utils.config.base import (
    BaseConfig,
    BaseTestingConfig,
    BaseProductionConfig,
    BaseDevelopmentLocalConfig,
    BaseTestLocalConfig
)
from lib.utils.config.env_types import EnvType, get_secret

# Импортируем все настройки из settings
from settings import *


if "CONFIG" not in os.environ:
    load_dotenv()


class Config(BaseConfig):
    ...


class TestingConfig(BaseTestingConfig, Config):
    ...


class ProductionConfig(BaseProductionConfig, Config):
    ...


class DevelopmentLocalConfig(BaseDevelopmentLocalConfig, Config):
    ...


class TestLocalConfig(BaseTestLocalConfig, Config):
    ...


CONFIG_MAP = {
    EnvType.TEST_LOCAL: TestLocalConfig,
    EnvType.DEVELOPMENT_LOCAL: DevelopmentLocalConfig,
    EnvType.TESTING: TestingConfig,
    EnvType.PRODUCTION: ProductionConfig,
}


def get_config() -> Config:
    config_name: str = get_secret("CONFIG")

    if config_name not in CONFIG_MAP:
        raise ValueError(f"Unknown config: {config_name}")

    env_type: EnvType = EnvType(config_name)
    config_class = CONFIG_MAP[env_type]

    return config_class()
