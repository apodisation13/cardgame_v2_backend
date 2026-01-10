from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from lib.utils.config.env_types import EnvType
from services.api.app.config import Config


def mount_static(
    app: FastAPI,
    config: Config,
) -> FastAPI:
    if config.ENV_TYPE in EnvType.docker_development():
        shared_media_root = "/shared_static/media"
        app.mount("/media", StaticFiles(directory=shared_media_root), name="media")
    elif config.ENV_TYPE == EnvType.DEVELOPMENT_LOCAL:
        base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
        shared_media_root = str(base_dir / "shared_static" / "media")
        app.mount("/media", StaticFiles(directory=shared_media_root), name="media")
    return app
