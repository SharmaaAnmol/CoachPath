"""
Centralized Exception Handlers for FastAPI.
Transforms all exceptions into RFC 7807 Problem Details compliant JSON responses.
"""

import logging
from typing import List
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import AppException
from app.schemas.error import ErrorDetail, ErrorPayload, ErrorResponse

logger = logging.getLogger(__name__)


def get_request_id(request: Request) -> str:
    """Helper to retrieve correlation ID from request state."""
    return getattr(request.state, "request_id", "req_unknown")


def register_exception_handlers(app: FastAPI) -> None:
    """Registers global exception handlers on the FastAPI application."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        request_id = get_request_id(request)
        logger.warning(f"[{request_id}] AppException: {exc.code} - {exc.message}")

        payload = ErrorResponse(
            error=ErrorPayload(
                code=exc.code,
                message=exc.message,
                status=exc.status_code,
                details=exc.details,
                request_id=request_id,
            )
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=payload.model_dump(),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        request_id = get_request_id(request)
        code_map = {
            status.HTTP_400_BAD_REQUEST: "MALFORMED_REQUEST",
            status.HTTP_401_UNAUTHORIZED: "AUTHENTICATION_REQUIRED",
            status.HTTP_403_FORBIDDEN: "INSUFFICIENT_PERMISSIONS",
            status.HTTP_404_NOT_FOUND: "RESOURCE_NOT_FOUND",
            status.HTTP_405_METHOD_NOT_ALLOWED: "METHOD_NOT_ALLOWED",
            status.HTTP_409_CONFLICT: "STATE_CONFLICT",
            status.HTTP_429_TOO_MANY_REQUESTS: "RATE_LIMIT_EXCEEDED",
        }
        code = code_map.get(exc.status_code, "HTTP_ERROR")

        payload = ErrorResponse(
            error=ErrorPayload(
                code=code,
                message=str(exc.detail) if exc.detail else "HTTP error occurred.",
                status=exc.status_code,
                details=None,
                request_id=request_id,
            )
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=payload.model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        request_id = get_request_id(request)
        logger.info(f"[{request_id}] Validation Error: {exc.errors()}")

        details: List[ErrorDetail] = []
        for err in exc.errors():
            loc = ".".join(str(x) for x in err.get("loc", []) if x != "body")
            details.append(
                ErrorDetail(
                    field=loc or None,
                    issue=err.get("msg", "Invalid parameter value"),
                )
            )

        payload = ErrorResponse(
            error=ErrorPayload(
                code="VALIDATION_ERROR",
                message="Invalid request parameters provided.",
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                details=details,
                request_id=request_id,
            )
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=payload.model_dump(),
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        request_id = get_request_id(request)
        logger.error(f"[{request_id}] Database Error: {exc}", exc_info=True)

        # Sanitize internal SQL error to prevent information leakage
        payload = ErrorResponse(
            error=ErrorPayload(
                code="DATABASE_ERROR",
                message="A database error occurred while processing the request.",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details=None,
                request_id=request_id,
            )
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=payload.model_dump(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        request_id = get_request_id(request)
        logger.error(f"[{request_id}] Unhandled Exception: {exc}", exc_info=True)

        payload = ErrorResponse(
            error=ErrorPayload(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected server error occurred. Please try again later.",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details=None,
                request_id=request_id,
            )
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=payload.model_dump(),
        )
