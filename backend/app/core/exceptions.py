"""
Custom Domain Exceptions for CoachPath.
Enables consistent error mapping across services and repositories.
"""

from typing import Any, List, Optional
from app.schemas.error import ErrorDetail


class AppException(Exception):
    """Base application exception with RFC 7807 problem details mapping."""

    def __init__(
        self,
        status_code: int = 500,
        code: str = "INTERNAL_SERVER_ERROR",
        message: str = "An unexpected server error occurred.",
        details: Optional[List[ErrorDetail]] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


class NotFoundException(AppException):
    """Exception raised when a requested resource is not found (404)."""

    def __init__(
        self,
        resource: str = "Resource",
        identifier: Optional[Any] = None,
        message: Optional[str] = None,
    ) -> None:
        msg = message or (
            f"{resource} with identifier '{identifier}' was not found."
            if identifier
            else f"{resource} not found."
        )
        super().__init__(
            status_code=404,
            code="RESOURCE_NOT_FOUND",
            message=msg,
        )


class ConflictException(AppException):
    """Exception raised when an operation conflicts with existing state (409)."""

    def __init__(
        self,
        message: str = "A state conflict occurred with existing resources.",
        details: Optional[List[ErrorDetail]] = None,
    ) -> None:
        super().__init__(
            status_code=409,
            code="STATE_CONFLICT",
            message=message,
            details=details,
        )


class UnauthorizedException(AppException):
    """Exception raised when authentication is required or invalid (401)."""

    def __init__(
        self,
        message: str = "Authentication is required to access this resource.",
    ) -> None:
        super().__init__(
            status_code=401,
            code="AUTHENTICATION_REQUIRED",
            message=message,
        )


class ForbiddenException(AppException):
    """Exception raised when permissions are insufficient (403)."""

    def __init__(
        self,
        message: str = "You do not have permission to access or modify this resource.",
    ) -> None:
        super().__init__(
            status_code=403,
            code="INSUFFICIENT_PERMISSIONS",
            message=message,
        )


class ValidationException(AppException):
    """Exception raised on domain validation failure (422)."""

    def __init__(
        self,
        message: str = "Invalid request parameters provided.",
        details: Optional[List[ErrorDetail]] = None,
    ) -> None:
        super().__init__(
            status_code=422,
            code="VALIDATION_ERROR",
            message=message,
            details=details,
        )


class ServiceUnavailableException(AppException):
    """Exception raised when required infrastructure is unreachable (503)."""

    def __init__(
        self,
        service_name: str = "Infrastructure component",
        message: Optional[str] = None,
    ) -> None:
        super().__init__(
            status_code=503,
            code="SERVICE_UNAVAILABLE",
            message=message or f"{service_name} is currently unavailable.",
        )
