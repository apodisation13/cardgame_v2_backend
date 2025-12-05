from lib.utils.config.base import (
    BaseConfig,
    BaseDevelopmentLocalConfig,
    BaseProductionConfig,
    BaseTestLocalConfig,
    BaseTestingConfig,
)
from lib.utils.config.env_types import EnvType, get_secret, load_env


load_env()


class Config(BaseConfig):
    AAA = "asdsadasdasdasdaassssssssssssssssssssssssssssssssssssss"


class TestingConfig(BaseTestingConfig, Config): ...


class ProductionConfig(BaseProductionConfig, Config): ...


class DevelopmentLocalConfig(BaseDevelopmentLocalConfig, Config): ...


class TestLocalConfig(BaseTestLocalConfig, Config): ...


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

    env_type = EnvType(config_name)
    config_class = CONFIG_MAP[env_type]

    return config_class()
