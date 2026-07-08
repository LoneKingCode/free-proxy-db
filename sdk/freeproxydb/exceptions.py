from __future__ import annotations

from typing import Any, Optional


class FreeProxyDBError(Exception):
    """Base SDK error."""


class ApiError(FreeProxyDBError):
    """API returned an HTTP error or non-success JSON envelope."""

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        detail: Any = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail

    def __str__(self) -> str:
        if self.status_code is not None:
            return f"[{self.status_code}] {super().__str__()}"
        return super().__str__()


class AuthenticationError(ApiError):
    """Missing or invalid API key."""


class AuthorizationError(ApiError):
    """API key disabled, expired, or not allowed for this endpoint/IP."""


class RateLimitError(ApiError):
    """Rate limit or quota exceeded."""
