from __future__ import annotations

from typing import Any, List, Optional, Union

from freeproxydb._http import DEFAULT_BASE_URL, BaseHttpClient
from freeproxydb._utils import https_param, join_csv
from freeproxydb._web_crawler import (
    HeadersInput,
    WebCrawlerProtocol,
    build_web_crawler_params,
)
from freeproxydb.exceptions import AuthenticationError
from freeproxydb.public import FilterValue, PublicClient


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
        method: str = "GET",
        headers: HeadersInput = None,
        cookie: Optional[str] = None,
        body: Optional[str] = None,
    ) -> str:
        """Fetch a URL via the authenticated crawler. Returns the response body text.

        Same routing engine as :meth:`PublicClient.web_crawler` (HTTP / SOCKS /
        Xray pool with ``protocol=auto``), but uses the high-quality pool and
        per-API-key quotas instead of per-IP limits.

        Supports ``method``, ``headers`` (dict or JSON string), ``cookie``, and
        ``body`` (POST only) for production scraping workflows.
        """
        params = build_web_crawler_params(
            url,
            protocol,
            timeout=timeout,
            method=method,
            headers=headers,
            cookie=cookie,
            body=body,
        )
        return self.get_json("/user/web_crawler", params=params)
