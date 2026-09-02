from __future__ import annotations

from typing import Any, Iterable, List, Optional, Union

from freeproxydb._http import BaseHttpClient, DEFAULT_BASE_URL
from freeproxydb._utils import https_param, join_csv
from freeproxydb._web_crawler import (
    HeadersInput,
    WebCrawlerProtocol,
    WebCrawlerResult,
    build_web_crawler_payload,
)

FilterValue = Union[str, Iterable[str], None]


class PublicClient(BaseHttpClient):
    """Client for public `/proxy/*` endpoints (no API key required)."""

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
    ):
        super().__init__(base_url=base_url, timeout=timeout)

    def search(
        self,
        *,
        country: FilterValue = "",
        protocol: FilterValue = "",
        anonymity: FilterValue = "",
        speed: str = "",
        https: Optional[Union[bool, int, str]] = None,
        page_index: int = 1,
        page_size: int = 10,
        order_by: str = "id",
        order_dir: str = "desc",
    ) -> dict[str, Any]:
        """Paginated proxy search. Returns `{total_count, data}`."""
        return self.get_json(
            "/proxy/search",
            params={
                "country": join_csv(country),
                "protocol": join_csv(protocol),
                "anonymity": join_csv(anonymity),
                "speed": speed,
                "https": https_param(https),
                "page_index": page_index,
                "page_size": page_size,
                "order_by": order_by,
                "order_dir": order_dir,
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
        """Fetch a plain-text subscription feed (`original` or base64 `v2ray`)."""
        return self.get_text(
            "/proxy/subscribe",
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

    def statistics(self) -> dict[str, Any]:
        """Basic pool statistics (country/protocol counts, last check time)."""
        return self.get_json("/proxy/statistics")

    def total_statistics(self) -> dict[str, Any]:
        """Extended statistics including country/protocol breakdown."""
        return self.get_json("/proxy/total_statistics")

    def client_ip(self) -> dict[str, Any]:
        """Return the caller IP as seen by the API."""
        return self.get_json("/proxy/client_ip")

    def anon_check(self) -> dict[str, Any]:
        """Check request headers and IP anonymity level."""
        return self.get_json("/proxy/anon_check")

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
        encoding: Optional[str] = None,
    ) -> WebCrawlerResult:
        """Fetch a URL through the public crawler.

        Returns ``{"status_code": int, "body": str}`` for the target response.
        ``status=1`` from the API means the proxy fetch completed; inspect
        ``status_code`` for the upstream HTTP status.

        Optional ``encoding`` forces response body decoding (e.g. ``gbk`` /
        ``gb18030``) when auto-detection fails on Chinese sites.

        Routes through HTTP, SOCKS, and/or the internal Xray pool depending on
        ``protocol``:

        - ``http`` — random HTTP proxy from the validated pool
        - ``socks`` — SOCKS pool plus Xray share-link nodes when available
        - ``auto`` — full routing with automatic retries (recommended)

        Optional ``method``, ``headers`` (dict or JSON string), ``cookie``, and
        ``body`` (POST only) customize the outbound request. Subject to per-IP
        rate limits.
        """
        payload = build_web_crawler_payload(
            url,
            protocol,
            timeout=timeout,
            method=method,
            headers=headers,
            cookie=cookie,
            body=body,
            encoding=encoding,
        )
        return self.post_json("/proxy/web_crawler", json=payload)

    def proxy_checker(
        self,
        servers: List[str],
        *,
        timeout: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        """Check one or more full proxy URLs (max 100)."""
        payload: dict[str, Any] = {"servers": servers}
        if timeout is not None:
            payload["timeout"] = timeout
        return self.post_json("/proxy/proxy_checker", json=payload)

    def ip_checker(
        self,
        ip: str,
        *,
        original_info: bool = True,
    ) -> dict[str, Any]:
        """Look up geo/ASN details for an IP address."""
        return self.get_json(
            "/proxy/ip_checker",
            params={"ip": ip, "original_info": original_info},
        )

    def port_checker(
        self,
        ip: str,
        ports: Union[str, Iterable[int]],
        *,
        timeout: Optional[int] = None,
    ) -> dict[str, Any]:
        """Scan ports on a host. `ports` as comma string or iterable of ints."""
        if isinstance(ports, str):
            ports_param = ports
        else:
            ports_param = ",".join(str(p) for p in ports)

        params: dict[str, Any] = {"ip": ip, "ports": ports_param}
        if timeout is not None:
            params["timeout"] = timeout
        return self.get_json("/proxy/port_checker", params=params)
