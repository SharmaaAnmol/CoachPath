"""
Correlation ID and Request Tracing Middleware.
Ensures every request has a unique correlation ID for end-to-end auditability.
"""

import time
import uuid
import logging
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware attaching X-Request-ID correlation headers to requests and responses."""

    HEADER_NAME = "X-Request-ID"

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract existing header or generate a new tracking ID
        request_id = request.headers.get(self.HEADER_NAME)
        if not request_id:
            request_id = f"req_{uuid.uuid4().hex[:14]}"

        request.state.request_id = request_id

        start_time = time.perf_counter()
        response: Response = await call_next(request)
        process_time_ms = (time.perf_counter() - start_time) * 1000

        # Inject correlation header in response
        response.headers[self.HEADER_NAME] = request_id
        response.headers["X-Process-Time-Ms"] = f"{process_time_ms:.2f}"

        logger.info(
            f"[{request_id}] {request.method} {request.url.path} "
            f"- {response.status_code} ({process_time_ms:.2f}ms)"
        )

        return response
