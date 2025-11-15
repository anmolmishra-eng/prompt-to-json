"""
Structured error response schemas following RFC 7807 Problem Details for HTTP APIs.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ErrorCode(str, Enum):
    """Standard error codes for the API"""

    # Authentication & Authorization
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"

    # Validation
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    PAYLOAD_TOO_LARGE = "PAYLOAD_TOO_LARGE"

    # Resource
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    RESOURCE_EXHAUSTED = "RESOURCE_EXHAUSTED"

    # Server
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    DATABASE_ERROR = "DATABASE_ERROR"

    # Business Logic
    INVALID_SPEC = "INVALID_SPEC"
    COMPLIANCE_FAILED = "COMPLIANCE_FAILED"
    LM_ERROR = "LM_ERROR"
    STORAGE_ERROR = "STORAGE_ERROR"


class FieldError(BaseModel):
    """Field-level validation error"""

    field: str = Field(..., description="Field name that failed validation")
    message: str = Field(..., description="Error message for this field")
    value: Optional[Any] = Field(None, description="The invalid value")


class ErrorDetail(BaseModel):
    """Error details with context"""

    code: ErrorCode = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error context")
    field_errors: Optional[List[FieldError]] = Field(None, description="Field-level validation errors")
    request_id: Optional[str] = Field(None, description="Trace ID for debugging")
    timestamp: Optional[str] = Field(None, description="When error occurred (ISO 8601)")


class ErrorResponse(BaseModel):
    """Standard API error response"""

    error: ErrorDetail = Field(..., description="Error information")

    class Config:
        schema_extra = {
            "example": {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "field_errors": [{"field": "prompt", "message": "Field is required", "value": None}],
                    "request_id": "req_abc123xyz",
                    "timestamp": "2025-11-15T12:46:00Z",
                }
            }
        }
