from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
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
            },
        },
        headers={
            "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
            "Access-Control-Allow-Credentials": "true",
        },
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
            },
        },
        headers={
            "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
            "Access-Control-Allow-Credentials": "true",
        },
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """
    Обработчик ошибок валидации Pydantic (422 Unprocessable Entity)

    Преобразует сложную структуру ошибок Pydantic в понятный для фронтенда формат
    """

    def extract_validation_errors(errors: list[dict[str, Any]]) -> list[dict[str, str]]:
        """Извлекает и форматирует ошибки валидации"""
        formatted_errors = []

        for error in errors:
            # Получаем путь к полю (например: ['body', 'username'])
            loc = error.get("loc", [])

            # Пропускаем первые элементы если это 'body' или 'query' или 'path'
            if loc and loc[0] in ("body", "query", "path"):
                field_path = ".".join(str(item) for item in loc[1:])
            else:
                field_path = ".".join(str(item) for item in loc) if loc else "unknown"

            # Берем сообщение об ошибке
            msg = error.get("msg", "Validation error")
            error_type = error.get("type", "validation_failed")

            # Форматируем человекочитаемое сообщение
            readable_msg = format_validation_message(msg, error_type, field_path)

            formatted_errors.append(
                {
                    "field": field_path,
                    "message": readable_msg,
                    "type": error_type,
                    "original_message": msg,
                },
            )

        return formatted_errors

    def format_validation_message(msg: str, error_type: str, field_path: str) -> str:
        """Форматирует сообщение об ошибке для пользователя"""

        # Преобразуем snake_case в нормальный текст
        field_name = field_path.replace("_", " ").title() if field_path else "Field"

        # Обрабатываем разные типы ошибок
        if error_type == "missing":
            return f"Поле '{field_name}' обязательно для заполнения"
        elif error_type == "string_too_short":
            if "min_length" in msg:
                min_len = msg.split("min_length=")[1].split(",")[0]
                return f"Поле '{field_name}' должно содержать минимум {min_len} символов"
        elif error_type == "string_too_long":
            if "max_length" in msg:
                max_len = msg.split("max_length=")[1].split(",")[0]
                return f"Поле '{field_name}' должно содержать не более {max_len} символов"
        elif error_type == "value_error":
            if "email" in field_path.lower():
                return f"Поле '{field_name}' должно содержать корректный email адрес"
            elif "url" in field_path.lower():
                return f"Поле '{field_name}' должно содержать корректный URL"
        elif "regex" in error_type:
            return f"Поле '{field_name}' содержит недопустимые символы или формат"

        # Дефолтное сообщение
        if field_path:
            return f"Ошибка в поле '{field_name}': {msg}"
        return msg

    # Извлекаем ошибки из исключения
    validation_errors = extract_validation_errors(exc.errors())

    # Группируем ошибки по полям (если нужно)
    field_errors = {}
    for error in validation_errors:
        if error["field"] not in field_errors:
            field_errors[error["field"]] = []
        field_errors[error["field"]].append(error["message"])

    # Создаем финальное сообщение
    if validation_errors:
        if len(validation_errors) == 1:
            error_summary = validation_errors[0]["message"]
        else:
            error_fields = [err["field"] for err in validation_errors]
            error_summary = f"Ошибки валидации в полях: {', '.join(error_fields)}"
    else:
        error_summary = "Ошибка валидации данных"

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": error_summary,
                "details": {
                    "validation_errors": validation_errors,
                },
            },
        },
        headers={
            "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
            "Access-Control-Allow-Credentials": "true",
        },
    )


def add_exceptions(app: FastAPI) -> FastAPI:
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(UserAlreadyExistsError, user_already_exists_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)
    return app
