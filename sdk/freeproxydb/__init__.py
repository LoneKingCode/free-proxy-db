"""FreeProxyDB Python SDK."""

from freeproxydb.exceptions import (
    ApiError,
    AuthenticationError,
    AuthorizationError,
    FreeProxyDBError,
    RateLimitError,
)
from freeproxydb.proxy_http import ProxyFetchResult, ProxyHttpClient, ProxyRequestError
from freeproxydb.proxy_pool import ProxyPool, ProxyPoolExhaustedError
from freeproxydb.public import PublicClient
from freeproxydb.user import UserClient
from freeproxydb._http import DEFAULT_BASE_URL

__all__ = [
    "PublicClient",
    "UserClient",
    "ProxyHttpClient",
    "ProxyFetchResult",
    "ProxyPool",
    "FreeProxyDBError",
    "ApiError",
    "AuthenticationError",
    "AuthorizationError",
    "RateLimitError",
    "ProxyRequestError",
    "ProxyPoolExhaustedError",
    "DEFAULT_BASE_URL",
]

__version__ = "0.1.0"
