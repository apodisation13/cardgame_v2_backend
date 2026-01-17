from pathlib import Path

from lib.utils.config.env_types import EnvType
from services.rest.app.config import Config, get_config


config: Config = get_config()

# общая папка проекта
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent

MEDIA_ROOT = ""
STATIC_ROOT = ""

if config.ENV_TYPE in EnvType.docker_development():
    MEDIA_ROOT = "/shared_static/media"
    STATIC_ROOT = "/shared_static/static"
elif config.ENV_TYPE == EnvType.DEVELOPMENT_LOCAL:
    SHARED_STATIC_DIR = BASE_DIR / "shared_static"
    MEDIA_ROOT = str(SHARED_STATIC_DIR / "media")
    STATIC_ROOT = str(SHARED_STATIC_DIR / "static")


MEDIA_URL = "/media/"
STATIC_URL = "/static/"
