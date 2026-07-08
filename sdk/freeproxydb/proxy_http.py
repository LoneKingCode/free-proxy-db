from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional, Union

import httpx

from freeproxydb._http import DEFAULT_BASE_URL
from freeproxydb.exceptions import FreeProxyDBError
from freeproxydb.public import FilterValue, PublicClient
from freeproxydb.proxy_pool import ProxyPool
from freeproxydb.proxy_url import https_filter_for_url, proxy_key, proxy_url_from_record
from freeproxydb.user import UserClient


class ProxyRequestError(FreeProxyDBError):
    """All proxy attempts failed for a target URL."""


@dataclass(frozen=True)
class ProxyFetchResult:
    """Result of a proxied HTTP request."""

    response: httpx.Response
    proxy_record: dict[str, Any]
    proxy_url: str
    attempts: int


class ProxyHttpClient:
    """
    HTTP client that routes requests through FreeProxyDB proxies with automatic
    failover (HTTP / SOCKS4 / SOCKS5 only).
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        country: FilterValue = "",
        protocol: FilterValue = "http,socks5,socks4",
        pool_size: int = 20,
        max_retries: int = 5,
        timeout: float = 30.0,
        verify: Union[bool, str] = False,
        follow_redirects: bool = True,
    ):
        self.timeout = timeout
        self.max_retries = max(1, max_retries)
        self.verify = verify
        self.follow_redirects = follow_redirects

        if api_key:
            self._api: Union[PublicClient, UserClient] = UserClient(
                api_key=api_key,
                base_url=base_url,
                timeout=timeout,
            )
            use_user_valid = True
        else:
            self._api = PublicClient(base_url=base_url, timeout=timeout)
            use_user_valid = False

        self._pool = ProxyPool(
            self._api,
            country=country,
            protocol=protocol,
            pool_size=pool_size,
            use_user_valid_proxies=use_user_valid,
        )

    def close(self) -> None:
        self._api.close()

    def __enter__(self) -> "ProxyHttpClient":
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Optional[Mapping[str, str]] = None,
        params: Optional[Mapping[str, Any]] = None,
        content: Optional[bytes] = None,
        data: Optional[Mapping[str, Any]] = None,
        json: Optional[Any] = None,
        max_retries: Optional[int] = None,
        https: Optional[bool] = None,
    ) -> ProxyFetchResult:
        retries = self.max_retries if max_retries is None else max(1, max_retries)
        https_filter = https if https is not None else https_filter_for_url(url)
        last_error: Optional[Exception] = None

        for attempt in range(1, retries + 1):
            record = self._pool.next(https=https_filter)
            proxy_url = proxy_url_from_record(record)
            try:
                with httpx.Client(
                    proxy=proxy_url,
                    timeout=self.timeout,
                    verify=self.verify,
                    follow_redirects=self.follow_redirects,
                ) as client:
                    response = client.request(
                        method,
                        url,
                        headers=headers,
                        params=params,
                        content=content,
                        data=data,
                        json=json,
                    )
                if response.status_code >= 400:
                    raise httpx.HTTPStatusError(
                        f"HTTP {response.status_code}",
                        request=response.request,
                        response=response,
                    )
                return ProxyFetchResult(
                    response=response,
                    proxy_record=record,
                    proxy_url=proxy_url,
                    attempts=attempt,
                )
            except Exception as exc:
                self._pool.mark_failed(record)
                last_error = exc

        message = f"request failed after {retries} proxy attempts: {url}"
        if last_error is not None:
            raise ProxyRequestError(message) from last_error
        raise ProxyRequestError(message)

    def get(self, url: str, **kwargs: Any) -> ProxyFetchResult:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> ProxyFetchResult:
        return self.request("POST", url, **kwargs)

    def get_text(self, url: str, **kwargs: Any) -> str:
        return self.get(url, **kwargs).response.text

    def get_json(self, url: str, **kwargs: Any) -> Any:
        return self.get(url, **kwargs).response.json()

    def fetch(
        self,
        url: str,
        *,
        method: str = "GET",
        **kwargs: Any,
    ) -> tuple[bool, Optional[str], str, Optional[dict[str, Any]]]:
        """
        Compatibility helper similar to ``proxy.http.proxy_fetch.ProxyFetchRouter.fetch``.

        Returns ``(success, body_text, message, proxy_record)``.
        """
        try:
            result = self.request(method, url, **kwargs)
            body = result.response.text
            if not body:
                return False, None, "empty response", result.proxy_record
            proxy_label = proxy_key(result.proxy_record)
            return True, body, f"success via {proxy_label}", result.proxy_record
        except Exception as exc:
            return False, None, f"error:{exc}", None
