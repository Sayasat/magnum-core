from typing import Any


class AppException(Exception):
    status_code: int = 500
    error_code: str = "INTERNAL_SERVER_ERROR"
    message: str = "Internal server error"

    def __init__(
        self,
        message: str | None = None,
        *,
        details: Any | None = None,
    ):
        self.message = message or self.message
        self.details = details
        super().__init__(self.message)


class BadRequestException(AppException):
    status_code = 400
    error_code = "BAD_REQUEST"
    message = "Bad request"


class UnauthorizedException(AppException):
    status_code = 401
    error_code = "UNAUTHORIZED"
    message = "Unauthorized"


class ForbiddenException(AppException):
    status_code = 403
    error_code = "FORBIDDEN"
    message = "Forbidden"


class NotFoundException(AppException):
    status_code = 404
    error_code = "NOT_FOUND"
    message = "Resource not found"


class ConflictException(AppException):
    status_code = 409
    error_code = "CONFLICT"
    message = "Resource already exists"


class ValidationException(AppException):
    status_code = 422
    error_code = "VALIDATION_ERROR"
    message = "Validation error"