from lib.utils.config.base import (
    BaseConfig,
    BaseDevelopmentLocalConfig,
    BaseDockerLocalConfig,
    BaseProductionConfig,
    BaseTestLocalConfig,
    BaseTestingConfig,
)
from lib.utils.config.env_types import EnvType, get_secret, load_env


load_env()


class Config(BaseConfig):
    USER_PASSWORD_SECRET_KEY: str = get_secret("USER_PASSWORD_SECRET_KEY", default="your-secret-key-here")
    ALGORITHM: str = get_secret("ALGORITHM", default="HS256")

    DB_USER: str = get_secret("DB_USER")
    DB_PASSWORD: str = get_secret("DB_PASSWORD")
    DB_HOST: str = get_secret("DB_HOST", default="localhost")
    DB_PORT: int = get_secret("DB_PORT", default=5432, cast=int)
    DB_NAME: str = get_secret("DB_NAME")
    DB_URL: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


class TestingConfig(BaseTestingConfig, Config): ...


class ProductionConfig(BaseProductionConfig, Config): ...


class DevelopmentLocalConfig(BaseDevelopmentLocalConfig, Config): ...


class TestLocalConfig(BaseTestLocalConfig, Config): ...


class DockerLocalConfig(BaseDockerLocalConfig, Config): ...


CONFIG_MAP = {
    EnvType.DEVELOPMENT_LOCAL: DevelopmentLocalConfig,
    EnvType.DOCKER_LOCAL: DockerLocalConfig,
    EnvType.PRODUCTION: ProductionConfig,
    EnvType.TESTING: TestingConfig,
    EnvType.TEST_LOCAL: TestLocalConfig,
}


def get_config() -> Config:
    config_name: str = get_secret("CONFIG")

    if config_name not in CONFIG_MAP:
        raise ValueError(f"Unknown config: {config_name}")

    env_type = EnvType(config_name)
    config_class = CONFIG_MAP[env_type]

    return config_class()
