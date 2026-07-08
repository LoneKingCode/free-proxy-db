from __future__ import annotations

import json
from typing import Any, Mapping, MutableMapping, Optional

import httpx

from freeproxydb.exceptions import (
    ApiError,
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
)

DEFAULT_BASE_URL = "https://freeproxydb.com/api"


class BaseHttpClient:
    """Shared HTTP layer for public and user API clients."""

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
        headers: Optional[Mapping[str, str]] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

        request_headers: MutableMapping[str, str] = {"Accept": "application/json"}
        if api_key:
            request_headers["X-API-KEY"] = api_key
        if headers:
            request_headers.update(headers)

        self._client = httpx.Client(
            base_url=self.base_url,
            headers=request_headers,
            timeout=timeout,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "BaseHttpClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.is_success:
            return

        detail: Any
        try:
            payload = response.json()
            detail = payload.get("detail", payload)
        except (json.JSONDecodeError, ValueError):
            detail = response.text

        message = detail if isinstance(detail, str) else str(detail)
        status_code = response.status_code

        if status_code in (401,):
            raise AuthenticationError(message, status_code=status_code, detail=detail)
        if status_code in (403,):
            raise AuthorizationError(message, status_code=status_code, detail=detail)
        if status_code in (429,):
            raise RateLimitError(message, status_code=status_code, detail=detail)
        raise ApiError(message, status_code=status_code, detail=detail)

    def _unwrap_json(self, response: httpx.Response) -> Any:
        self._raise_for_status(response)
        try:
            payload = response.json()
        except (json.JSONDecodeError, ValueError) as exc:
            raise ApiError(
                "Invalid JSON response",
                status_code=response.status_code,
                detail=response.text,
            ) from exc

        if not isinstance(payload, dict):
            return payload

        status = payload.get("status")
        if status is not None and status != 1:
            message = payload.get("message") or "API request failed"
            raise ApiError(message, status_code=response.status_code, detail=payload)

        if "data" in payload:
            return payload["data"]
        return payload

    def get_json(self, path: str, *, params: Optional[Mapping[str, Any]] = None) -> Any:
        response = self._client.get(path, params=params)
        return self._unwrap_json(response)

    def get_text(self, path: str, *, params: Optional[Mapping[str, Any]] = None) -> str:
        response = self._client.get(
            path,
            params=params,
            headers={"Accept": "text/plain, */*"},
        )
        self._raise_for_status(response)
        return response.text

    def post_json(
        self,
        path: str,
        *,
        json: Optional[Mapping[str, Any]] = None,
        params: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        response = self._client.post(path, json=json, params=params)
        return self._unwrap_json(response)
