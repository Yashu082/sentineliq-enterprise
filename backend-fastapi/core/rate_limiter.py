from __future__ import annotations

import time
from collections import defaultdict
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


class RateLimiter:
    """
    Simple in-memory rate limiter using token bucket algorithm.
    In production, use Redis or similar for distributed rate limiting.
    """

    def __init__(self, requests_per_minute: int = 60) -> None:
        self.requests_per_minute = requests_per_minute
        self.requests: defaultdict[str, list[float]] = defaultdict(list)
        self.window = 60  # 60 seconds window

    def is_allowed(self, identifier: str) -> bool:
        """Check if the request is allowed based on rate limit."""
        now = time.time()
        
        # Clean up old requests outside the window
        self.requests[identifier] = [
            timestamp for timestamp in self.requests[identifier]
            if now - timestamp < self.window
        ]
        
        # Check if under limit
        if len(self.requests[identifier]) >= self.requests_per_minute:
            return False
        
        # Add current request
        self.requests[identifier].append(now)
        return True

    def get_remaining_requests(self, identifier: str) -> int:
        """Get remaining requests for the identifier."""
        now = time.time()
        self.requests[identifier] = [
            timestamp for timestamp in self.requests[identifier]
            if now - timestamp < self.window
        ]
        return max(0, self.requests_per_minute - len(self.requests[identifier]))


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=60)


async def rate_limit_middleware(request: Request, call_next: Any) -> JSONResponse:
    """
    FastAPI middleware for rate limiting.
    Rate limits based on user_hash from JWT token or IP address.
    """
    # Try to get user_hash from token, otherwise use IP
    identifier = request.client.host if request.client else "unknown"
    
    # Check if user is authenticated
    if "authorization" in request.headers:
        # In a real implementation, decode the token to get user_hash
        # For now, use the token as identifier
        identifier = request.headers["authorization"][:50]  # Truncated for safety
    
    if not rate_limiter.is_allowed(identifier):
        remaining = rate_limiter.get_remaining_requests(identifier)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "remaining": remaining,
                "limit": rate_limiter.requests_per_minute,
            },
        )
    
    response = await call_next(request)
    
    # Add rate limit headers
    remaining = rate_limiter.get_remaining_requests(identifier)
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.requests_per_minute)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)
    
    return response
