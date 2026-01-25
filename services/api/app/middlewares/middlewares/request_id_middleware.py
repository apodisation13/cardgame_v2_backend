from collections.abc import Callable
import uuid

import elasticapm
from fastapi import FastAPI, Request, Response
from lib.utils.config.env_types import EnvType
from lib.utils.elk.request_id import request_id_var
from services.api.app.config import Config


async def request_id_middleware(
    request: Request,
    call_next: Callable,
) -> Response:
    request_id_header = request.headers.get("X-Request-ID")

    if request_id_header:
        request_id = request_id_header
    else:
        request_id = str(uuid.uuid4())

    request_id_var.set(request_id)

    elasticapm.label(request_id=request_id)

    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    finally:
        request_id_var.set(None)


def add_request_id_middleware(
    app: FastAPI,
    config: Config,
) -> FastAPI:
    if config.ENV_TYPE in EnvType.need_elastic():
        app.middleware("http")(request_id_middleware)
    return app
