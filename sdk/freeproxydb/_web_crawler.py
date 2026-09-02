from __future__ import annotations

from typing import Any, Literal, Mapping, Optional, TypedDict, Union

WebCrawlerProtocol = Literal["http", "socks", "auto"]
WebCrawlerMethod = Literal["GET", "POST"]

HeadersInput = Union[Mapping[str, str], str, None]


class WebCrawlerResult(TypedDict):
    """Unwrapped ``data`` from POST /proxy|user/web_crawler."""

    status_code: int
    body: str


_FORBIDDEN_HEADERS = frozenset(
    {
        "host",
        "content-length",
        "transfer-encoding",
        "connection",
        "keep-alive",
        "proxy-authorization",
        "te",
        "trailer",
        "upgrade",
    }
)
_MAX_HEADERS = 30
_MAX_HEADER_VALUE_LEN = 4096
_MAX_COOKIE_LEN = 8192
_MAX_BODY_LEN = 65536


def normalize_web_crawler_method(method: str) -> WebCrawlerMethod:
    normalized = (method or "GET").upper()
    if normalized not in ("GET", "POST"):
        raise ValueError("method must be GET or POST")
    return normalized  # type: ignore[return-value]


def normalize_web_crawler_protocol(protocol: str) -> WebCrawlerProtocol:
    normalized = (protocol or "").lower()
    if normalized not in ("http", "socks", "auto"):
        raise ValueError('protocol must be "http", "socks", or "auto"')
    return normalized  # type: ignore[return-value]


def _normalize_headers(headers: HeadersInput) -> Optional[dict[str, str]]:
    if headers is None:
        return None
    if isinstance(headers, str):
        import json

        raw = headers.strip()
        if not raw:
            return None
        try:
            parsed = json.loads(raw)
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid headers JSON: {exc}") from exc
        if not isinstance(parsed, dict):
            raise ValueError("headers must be a JSON object")
        headers = parsed

    if len(headers) > _MAX_HEADERS:
        raise ValueError(f"headers exceeds max {_MAX_HEADERS} entries")

    encoded: dict[str, str] = {}
    for key, value in headers.items():
        if not isinstance(key, str) or not key.strip():
            raise ValueError("Invalid header name")
        if not isinstance(value, str):
            raise ValueError(f"Header {key!r} value must be a string")
        name = key.strip()
        if name.lower() in _FORBIDDEN_HEADERS:
            raise ValueError(f"Header {name!r} is not allowed")
        if len(value) > _MAX_HEADER_VALUE_LEN:
            raise ValueError(f"Header {name!r} value exceeds max length")
        encoded[name] = value

    return encoded or None


def build_web_crawler_payload(
    url: str,
    protocol: str,
    *,
    timeout: Optional[int] = None,
    method: str = "GET",
    headers: HeadersInput = None,
    cookie: Optional[str] = None,
    body: Optional[str] = None,
    encoding: Optional[str] = None,
) -> dict[str, Any]:
    """Build JSON body for POST ``/proxy/web_crawler`` and ``/user/web_crawler``."""
    if not url or not url.strip():
        raise ValueError("url is required")

    http_method = normalize_web_crawler_method(method)
    routing = normalize_web_crawler_protocol(protocol)

    if timeout is not None and (timeout <= 0 or timeout > 60):
        raise ValueError("timeout must be between 1 and 60 seconds")

    if body is not None and len(body) > _MAX_BODY_LEN:
        raise ValueError("body exceeds max length")
    if http_method == "GET" and body:
        raise ValueError("body is only allowed with POST")

    if cookie is not None and len(cookie) > _MAX_COOKIE_LEN:
        raise ValueError("cookie exceeds max length")

    if encoding is not None and str(encoding).strip():
        try:
            import codecs

            codecs.lookup(str(encoding).strip())
        except LookupError as exc:
            raise ValueError(f"Unsupported encoding: {encoding}") from exc

    payload: dict[str, Any] = {
        "url": url.strip(),
        "protocol": routing,
        "method": http_method,
    }
    if timeout is not None:
        payload["timeout"] = timeout

    headers_obj = _normalize_headers(headers)
    if headers_obj:
        payload["headers"] = headers_obj
    if cookie:
        payload["cookie"] = cookie.strip()
    if body is not None:
        payload["body"] = body
    if encoding is not None and str(encoding).strip():
        payload["encoding"] = str(encoding).strip()

    return payload


# Backwards-compatible alias used by older imports/tests in this repo.
build_web_crawler_params = build_web_crawler_payload
