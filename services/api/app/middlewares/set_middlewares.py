from fastapi import FastAPI
from lib.utils.elk.elastic_tracer import ElasticTracerManager
from services.api.app.config import Config
from services.api.app.middlewares.middlewares.apm_middleware import add_apm_middleware
from services.api.app.middlewares.middlewares.cors_middleware import add_cors_middleware
from services.api.app.middlewares.middlewares.logging_middleware import add_logging_middleware
from services.api.app.middlewares.middlewares.request_id_middleware import add_request_id_middleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware


def set_middlewares(
    app: FastAPI,
    config: Config,
    apm_manager: ElasticTracerManager,
) -> FastAPI:
    add_cors_middleware(app)
    app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
    add_logging_middleware(app)
    add_request_id_middleware(app, config)
    add_apm_middleware(app, config, apm_manager)
    return app
