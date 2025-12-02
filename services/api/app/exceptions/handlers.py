from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from services.api.app.exceptions import UserAlreadyExistsError


async def global_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": exc.__class__.__name__,
                "details": exc.__repr__(),
            }
        }
    )


async def user_already_exists_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    if "username" in str(exc):
        message = " Field {username} already exists"
    elif "email" in str(exc):
        message = "Field {email} already exists"
    else:
        message = "Unknown error"

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "BAD_REQUEST",
                "message": message,
                "details": exc.__repr__(),
            }
        }
    )


def add_exceptions(app: FastAPI) -> FastAPI:
    app.add_exception_handler(Exception, global_exception_handler)
    app.add_exception_handler(UserAlreadyExistsError, user_already_exists_exception_handler)
    return app
