"""Uniform error envelope: {"error": {"code": ..., "message": ..., "details": [...] | null}}.

Raw exception text, SQL errors and stack traces are logged server-side but never sent to clients.
"""
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.errors import AppError

logger = logging.getLogger("app.errors")


def error_response(status_code: int, code: str, message: str, details: list[dict] | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "details": details}},
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError):
        return error_response(exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError):
        details = []
        for err in exc.errors():
            loc = ".".join(str(part) for part in err.get("loc", ()))
            message = str(err.get("msg", "Invalid value")).removeprefix("Value error, ")
            details.append({"field": loc, "message": message, "type": err.get("type", "value_error")})
        return error_response(422, "validation_error", "Request validation failed.", details)

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(_: Request, exc: StarletteHTTPException):
        message = exc.detail if isinstance(exc.detail, str) else "HTTP error"
        return error_response(exc.status_code, f"http_{exc.status_code}", message)

    @app.exception_handler(IntegrityError)
    async def handle_integrity_error(_: Request, exc: IntegrityError):
        logger.warning("Database integrity error: %s", exc.orig)
        return error_response(409, "integrity_error", "The request conflicts with existing data.")

    @app.exception_handler(OperationalError)
    async def handle_operational_error(_: Request, exc: OperationalError):
        logger.error("Database operational error: %s", exc.orig)
        return error_response(503, "database_unavailable", "The database is temporarily unavailable. Please retry.")

    @app.exception_handler(Exception)
    async def handle_unexpected(_: Request, exc: Exception):
        logger.exception("Unhandled error", exc_info=exc)
        return error_response(500, "internal_error", "An unexpected error occurred.")
