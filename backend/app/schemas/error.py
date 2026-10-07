"""
Standardized RFC 7807 Problem Details and Error Response Schemas.
"""

from typing import Any, List, Optional
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Detailed context for a specific validation issue or parameter."""

    field: Optional[str] = Field(None, description="Affected field name or parameter")
    issue: str = Field(..., description="Explanation of the issue")


class ErrorPayload(BaseModel):
    """Inner RFC 7807 problem details object."""

    code: str = Field(..., description="Machine-readable error code string")
    message: str = Field(..., description="Human-readable error description")
    status: int = Field(..., description="HTTP status code")
    details: Optional[List[ErrorDetail]] = Field(None, description="Granular issue list")
    request_id: Optional[str] = Field(None, description="Request correlation tracing ID")


class ErrorResponse(BaseModel):
    """Outer standard error envelope response."""

    error: ErrorPayload
