from elasticapm.contrib.starlette import ElasticAPM
from fastapi import FastAPI
from lib.utils.config.env_types import EnvType
from lib.utils.elk.elastic_tracer import ElasticTracerManager
from services.api.app.config import Config


def add_apm_middleware(
    app: FastAPI,
    config: Config,
    apm_manager: ElasticTracerManager,
) -> FastAPI:
    if config.ENV_TYPE in EnvType.need_elastic():
        app.add_middleware(
            ElasticAPM,
            client=apm_manager.client,
        )
    return app
