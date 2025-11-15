"""
Rate limiting middleware to prevent abuse and manage resource usage.
"""

import logging
import time
from collections import defaultdict
from typing import Optional

from fastapi import Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter using token bucket algorithm"""

    def __init__(self, requests_per_minute: int = 100):
        self.requests_per_minute = requests_per_minute
        self.clients = defaultdict(lambda: {"tokens": requests_per_minute, "last_update": time.time()})

    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed"""
        client = self.clients[client_id]
        now = time.time()
        elapsed = now - client["last_update"]

        # Refill tokens (1 token per 0.6 seconds = 100 per minute)
        refill_rate = self.requests_per_minute / 60.0
        tokens_to_add = elapsed * refill_rate

        client["tokens"] = min(self.requests_per_minute, client["tokens"] + tokens_to_add)
        client["last_update"] = now

        if client["tokens"] >= 1:
            client["tokens"] -= 1
            return True
        return False

    def get_remaining(self, client_id: str) -> int:
        """Get remaining requests for client"""
        return int(self.clients[client_id].get("tokens", 0))


rate_limiter = RateLimiter(requests_per_minute=100)


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""

    # Extract client identifier (IP or user ID)
    client_ip = request.client.host if request.client else "unknown"

    # Skip rate limiting for health checks
    if request.url.path in ["/api/v1/health", "/metrics"]:
        return await call_next(request)

    # Check rate limit
    if not rate_limiter.is_allowed(client_ip):
        logger.warning(f"Rate limit exceeded for client {client_ip}")

        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": {
                    "code": "RESOURCE_EXHAUSTED",
                    "message": "Too many requests. Please try again later.",
                    "details": {"retry_after": 60},
                }
            },
        )

    # Add rate limit headers to response
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.requests_per_minute)
    response.headers["X-RateLimit-Remaining"] = str(rate_limiter.get_remaining(client_ip))

    return response


# Payload size validation middleware
MAX_PAYLOAD_SIZE = 50 * 1024 * 1024  # 50 MB


async def payload_size_middleware(request: Request, call_next):
    """Validate request payload size"""

    if request.method in ["POST", "PUT", "PATCH"]:
        # Check Content-Length header
        content_length = request.headers.get("content-length")

        if content_length and int(content_length) > MAX_PAYLOAD_SIZE:
            logger.warning(
                f"Payload too large from {request.client.host}: " f"{content_length} bytes (max: {MAX_PAYLOAD_SIZE})"
            )

            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={
                    "error": {
                        "code": "PAYLOAD_TOO_LARGE",
                        "message": f"Request payload exceeds maximum size of {MAX_PAYLOAD_SIZE} bytes",
                        "details": {"max_size": MAX_PAYLOAD_SIZE, "received": int(content_length)},
                    }
                },
            )

    return await call_next(request)
