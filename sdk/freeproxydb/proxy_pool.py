from __future__ import annotations

import random
from collections import deque
from typing import Any, Deque, Optional, Set, Union

from freeproxydb.exceptions import FreeProxyDBError
from freeproxydb.public import FilterValue, PublicClient
from freeproxydb.proxy_url import proxy_key
from freeproxydb.user import UserClient

ApiClient = Union[PublicClient, UserClient]


class ProxyPoolExhaustedError(FreeProxyDBError):
    """No usable HTTP/SOCKS proxies left in the pool."""


class ProxyPool:
    """Fetch and rotate HTTP/SOCKS proxies from FreeProxyDB API."""

    def __init__(
        self,
        api_client: ApiClient,
        *,
        country: FilterValue = "",
        protocol: FilterValue = "http,socks5,socks4",
        pool_size: int = 20,
        use_user_valid_proxies: bool = False,
    ):
        self._api = api_client
        self._country = country
        self._protocol = protocol
        self._pool_size = max(1, min(pool_size, 100))
        self._use_user_valid = use_user_valid_proxies and isinstance(
            api_client, UserClient
        )
        self._queue: Deque[dict[str, Any]] = deque()
        self._failed: Set[str] = set()

    def refill(self, *, https: Optional[bool] = None) -> int:
        records = self._fetch_records(https=https)
        added = 0
        random.shuffle(records)
        for record in records:
            key = proxy_key(record)
            if key in self._failed:
                continue
            self._queue.append(record)
            added += 1
        return added

    def next(self, *, https: Optional[bool] = None) -> dict[str, Any]:
        if not self._queue:
            added = self.refill(https=https)
            if added == 0:
                raise ProxyPoolExhaustedError(
                    "no available HTTP/SOCKS proxies from API (pool exhausted)"
                )
        return self._queue.popleft()

    def mark_failed(self, record: dict[str, Any]) -> None:
        self._failed.add(proxy_key(record))

    def reset_failed(self) -> None:
        self._failed.clear()

    def _fetch_records(self, *, https: Optional[bool] = None) -> list[dict[str, Any]]:
        if self._use_user_valid:
            data = self._api.valid_proxies(
                count=self._pool_size,
                country=self._country,
                protocol=self._protocol,
                https=https,
                simple=False,
            )
            return list(data or [])

        page = self._api.search(
            country=self._country,
            protocol=self._protocol,
            https=https,
            page_index=1,
            page_size=self._pool_size,
            order_by="check_success_count",
            order_dir="desc",
        )
        return list((page or {}).get("data") or [])
