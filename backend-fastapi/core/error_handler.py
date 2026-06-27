from __future__ import annotations

import traceback
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from core.logging_config import get_logger

logger = get_logger(__name__)


class SentinelIQError(Exception):
    """Base exception for SentinelIQ application errors."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR", details: dict[str, Any] | None = None) -> None:
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)


class ValidationError(SentinelIQError):
    """Raised when input validation fails."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message, code="VALIDATION_ERROR", details=details)


class AuthenticationError(SentinelIQError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message, code="AUTHENTICATION_ERROR")


class AuthorizationError(SentinelIQError):
    """Raised when authorization fails."""

    def __init__(self, message: str = "Authorization failed") -> None:
        super().__init__(message, code="AUTHORIZATION_ERROR")


class RateLimitError(SentinelIQError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message, code="RATE_LIMIT_ERROR")


class LLMError(SentinelIQError):
    """Raised when LLM operations fail."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message, code="LLM_ERROR", details=details)


async def sentinel_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Central error handler for all exceptions.
    Provides consistent error responses and logging.
    """
    # Log the error
    logger.error(
        f"Error handling request {request.url.path}: {type(exc).__name__}: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
        },
    )

    # Handle SentinelIQ custom errors
    if isinstance(exc, SentinelIQError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        )

    # Handle HTTP exceptions from FastAPI
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP_ERROR",
                "message": exc.detail,
            },
        )

    # Handle unexpected errors
    logger.error(f"Unhandled exception: {traceback.format_exc()}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_ERROR",
            "message": "An unexpected error occurred. Please try again later.",
        },
    )
