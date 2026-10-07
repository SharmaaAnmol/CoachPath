"""
Rate Limiting & Abuse Prevention Utilities.
Implements sliding-window attempt tracking for authentication endpoints
to defend against credential stuffing and brute-force attacks.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Dict, List
from app.core.exceptions import AppException

# Default: 5 failed attempts within 15 minutes (900 seconds)
DEFAULT_MAX_ATTEMPTS = 5
DEFAULT_WINDOW_SECONDS = 900


class SlidingWindowRateLimiter:
    """In-memory sliding window rate limiter for authentication protection."""

    def __init__(self, max_attempts: int = DEFAULT_MAX_ATTEMPTS, window_seconds: int = DEFAULT_WINDOW_SECONDS):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._attempts: Dict[str, List[float]] = defaultdict(list)

    def _clean_expired(self, key: str, now: float) -> None:
        """Removes expired attempt timestamps outside the rolling window."""
        cutoff = now - self.window_seconds
        self._attempts[key] = [t for t in self._attempts[key] if t > cutoff]

    def check(self, key: str) -> None:
        """
        Validates whether key is currently rate-limited.
        Raises HTTP 429 AppException if threshold is exceeded.
        """
        now = time.time()
        self._clean_expired(key, now)
        if len(self._attempts[key]) >= self.max_attempts:
            raise AppException(
                status_code=429,
                code="RATE_LIMIT_EXCEEDED",
                message="Too many failed login attempts. Account temporarily locked for 15 minutes.",
            )

    def record_failure(self, key: str) -> None:
        """Records a failed authentication attempt."""
        now = time.time()
        self._clean_expired(key, now)
        self._attempts[key].append(now)

    def record_success(self, key: str) -> None:
        """Resets failed attempt records upon successful authentication."""
        if key in self._attempts:
            del self._attempts[key]

    def reset_all(self) -> None:
        """Clears all tracking data (useful for test teardown)."""
        self._attempts.clear()


# Global authentication rate limiter instance
auth_rate_limiter = SlidingWindowRateLimiter()
