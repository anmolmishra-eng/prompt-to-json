"""
Global exception handling and structured error responses.
Implements proper error handling for all edge cases.
"""

import logging
import uuid
from datetime import datetime
from typing import Optional

import sentry_sdk
from app.schemas.error_schemas import ErrorCode, ErrorDetail, ErrorResponse, FieldError
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class APIException(HTTPException):
    """Custom API exception with structured error details"""

    def __init__(
        self,
        status_code: int,
        error_code: ErrorCode,
        message: str,
        details: Optional[dict] = None,
        field_errors: Optional[list] = None,
    ):
        self.error_code = error_code
        self.message = message
        self.details = details
        self.field_errors = field_errors
        self.request_id = str(uuid.uuid4())[:12]
        super().__init__(status_code=status_code, detail=message)


def format_error_response(
    error_code: ErrorCode,
    message: str,
    status_code: int,
    details: Optional[dict] = None,
    field_errors: Optional[list] = None,
    request_id: Optional[str] = None,
) -> dict:
    """Format structured error response"""

    if not request_id:
        request_id = str(uuid.uuid4())[:12]

    error_detail = ErrorDetail(
        code=error_code,
        message=message,
        details=details,
        field_errors=field_errors,
        request_id=request_id,
        timestamp=datetime.utcnow().isoformat() + "Z",
    )

    return {"error": error_detail.model_dump(exclude_none=True)}


def register_exception_handlers(app: FastAPI):
    """Register all global exception handlers"""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle FastAPI validation errors"""

        logger.warning(f"Validation error on {request.url.path}: {exc}")

        # Extract field errors from validation errors
        field_errors = []
        for error in exc.errors():
            field_name = ".".join(str(x) for x in error["loc"][1:])
            field_errors.append(
                FieldError(
                    field=field_name,
                    message=error["msg"],
                    value=error.get("input"),
                ).model_dump()
            )

        response = format_error_response(
            error_code=ErrorCode.VALIDATION_ERROR,
            message="Request validation failed",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            field_errors=field_errors,
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=response,
        )

    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        """Handle custom API exceptions"""

        logger.error(
            f"API Exception on {request.url.path}: {exc.error_code} - {exc.message}",
            extra={"request_id": exc.request_id},
        )

        # Send to Sentry with request_id context
        with sentry_sdk.push_scope() as scope:
            scope.set_context("request_id", {"value": exc.request_id})
            sentry_sdk.capture_exception(exc)

        response = format_error_response(
            error_code=exc.error_code,
            message=exc.message,
            status_code=exc.status_code,
            details=exc.details,
            field_errors=exc.field_errors,
            request_id=exc.request_id,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=response,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions"""

        logger.error(f"HTTP Exception on {request.url.path}: {exc.detail}")

        # Map HTTP status codes to error codes
        error_code_map = {
            400: ErrorCode.INVALID_INPUT,
            401: ErrorCode.UNAUTHORIZED,
            403: ErrorCode.FORBIDDEN,
            404: ErrorCode.NOT_FOUND,
            409: ErrorCode.CONFLICT,
            429: ErrorCode.RESOURCE_EXHAUSTED,
            500: ErrorCode.INTERNAL_ERROR,
            503: ErrorCode.SERVICE_UNAVAILABLE,
        }

        error_code = error_code_map.get(exc.status_code, ErrorCode.INTERNAL_ERROR)

        response = format_error_response(
            error_code=error_code,
            message=str(exc.detail),
            status_code=exc.status_code,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=response,
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """Handle value errors from business logic"""

        logger.error(f"Value Error on {request.url.path}: {str(exc)}")

        sentry_sdk.capture_exception(exc)

        response = format_error_response(
            error_code=ErrorCode.INVALID_INPUT,
            message=f"Invalid value: {str(exc)}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=response,
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all unhandled exceptions"""

        request_id = str(uuid.uuid4())[:12]

        logger.exception(f"Unhandled exception on {request.url.path}", extra={"request_id": request_id}, exc_info=exc)

        # Send to Sentry
        with sentry_sdk.push_scope() as scope:
            scope.set_context("request_id", {"value": request_id})
            scope.set_context("path", {"value": request.url.path})
            sentry_sdk.capture_exception(exc)

        response = format_error_response(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="An unexpected error occurred. Please contact support.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_type": type(exc).__name__},
            request_id=request_id,
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response,
        )
