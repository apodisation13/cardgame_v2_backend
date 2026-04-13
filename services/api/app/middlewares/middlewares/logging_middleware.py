from collections.abc import Callable
import logging
import time

from fastapi import FastAPI, Request, Response
from lib.utils.elk.request_id import request_id_var


logger = logging.getLogger(__name__)


async def logging_middleware(
    request: Request,
    call_next: Callable,
) -> Response:
    start_time = time.time()

    method = (request.method).upper()
    url = str(request.url)
    client_host = request.client.host if request.client else "unknown"
    request_id = request_id_var.get()

    logger.info(
        "Request ← %s: %s",
        method,
        url,
        extra={
            "request_id": request_id,
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", ""),
            "method": method,
            "url": url,
            "client_host": client_host,
        },
    )

    try:
        response = await call_next(request)

        process_time = time.time() - start_time

        logger.info(
            "Response → %s: %s, status: %s",
            method,
            url,
            response.status_code,
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "duration": round(process_time, 3),
                "response_size": response.headers.get("content-length", 0),
            },
        )
        return response

    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            "Error ✗ %s: %s, Error: %s",
            method,
            url,
            str(e),
            extra={
                "request_id": request_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "duration": round(process_time, 3),
            },
        )
        raise


def add_logging_middleware(
    app: FastAPI,
) -> FastAPI:
    app.middleware("http")(logging_middleware)
    return app
