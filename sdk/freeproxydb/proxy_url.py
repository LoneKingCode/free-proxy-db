from __future__ import annotations

from typing import Any, Mapping

HTTP_PROTOCOLS = frozenset({"http", "https"})
SOCKS_PROTOCOLS = frozenset({"socks4", "socks5"})
SUPPORTED_PROTOCOLS = HTTP_PROTOCOLS | SOCKS_PROTOCOLS


def is_socks_proxy_url(proxy_url: str) -> bool:
    lowered = (proxy_url or "").lower()
    return lowered.startswith("socks4://") or lowered.startswith("socks5://")


def is_http_proxy_url(proxy_url: str) -> bool:
    lowered = (proxy_url or "").lower()
    return lowered.startswith("http://") or lowered.startswith("https://")


def proxy_key(record: Mapping[str, Any]) -> str:
    connect = (record.get("connect_string") or "").strip()
    if connect:
        return connect
    protocol = (record.get("protocol") or "http").lower()
    ip = record.get("ip")
    port = record.get("port")
    return f"{protocol}://{ip}:{port}"


def proxy_url_from_record(record: Mapping[str, Any]) -> str:
    connect = (record.get("connect_string") or "").strip()
    if connect:
        lowered = connect.lower()
        if lowered.startswith(("http://", "https://", "socks4://", "socks5://")):
            return connect
        raise ValueError(f"unsupported connect_string scheme: {connect}")

    protocol = (record.get("protocol") or "http").lower()
    ip = record.get("ip")
    port = record.get("port")
    if not ip or not port:
        raise ValueError("proxy record missing ip/port or connect_string")

    if protocol in SOCKS_PROTOCOLS:
        return f"{protocol}://{ip}:{port}"
    if protocol in HTTP_PROTOCOLS or protocol in {"mtproto", "vmess", "vless"}:
        # SDK HTTP client only supports classic HTTP/SOCKS; map unknown to http://
        return f"http://{ip}:{port}"
    return f"http://{ip}:{port}"


def https_filter_for_url(url: str) -> bool | None:
    if url.lower().startswith("https://"):
        return True
    return None
