from __future__ import annotations

from typing import Any, Iterable, List, Optional, Union

from freeproxydb._http import DEFAULT_BASE_URL, BaseHttpClient
from freeproxydb._utils import https_param, join_csv
from freeproxydb.exceptions import AuthenticationError
from freeproxydb.public import FilterValue, PublicClient

WebCrawlerProtocol = str  # "http" | "socks" | "auto"


class UserClient(PublicClient):
    """Client for authenticated `/user/*` endpoints (API key required)."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ):
        if not api_key or not api_key.strip():
            raise AuthenticationError("api_key is required for UserClient")
        self.api_key = api_key.strip()
        BaseHttpClient.__init__(
            self,
            base_url=base_url,
            api_key=self.api_key,
            timeout=timeout,
        )

    def valid_proxies(
        self,
        *,
        count: int = 10,
        country: FilterValue = "",
        protocol: FilterValue = "",
        https: Optional[Union[bool, int, str]] = None,
        simple: bool = False,
    ) -> List[dict[str, Any]]:
        """Return top valid high-quality proxies (requires API key)."""
        return self.get_json(
            "/user/valid_proxies",
            params={
                "count": count,
                "country": join_csv(country),
                "protocol": join_csv(protocol),
                "https": https_param(https),
                "simple": simple,
            },
        )

    def subscribe(
        self,
        *,
        country: FilterValue = "",
        protocol: FilterValue = "",
        anonymity: FilterValue = "",
        speed: str = "",
        https: Optional[Union[bool, int, str]] = None,
        count: int = 50,
        subscribe_format: str = "v2ray",
    ) -> str:
        """Authenticated subscription feed with higher count limits."""
        return self.get_text(
            "/user/subscribe",
            params={
                "country": join_csv(country),
                "protocol": join_csv(protocol),
                "anonymity": join_csv(anonymity),
                "speed": speed,
                "https": https_param(https),
                "count": count,
                "subscribe_format": subscribe_format,
            },
        )

    def web_crawler(
        self,
        url: str,
        protocol: WebCrawlerProtocol,
        *,
        timeout: Optional[int] = None,
    ) -> str:
        """Fetch a URL via authenticated crawler (per-key quotas apply)."""
        params: dict[str, Any] = {"url": url, "protocol": protocol}
        if timeout is not None:
            params["timeout"] = timeout
        return self.get_json("/user/web_crawler", params=params)
