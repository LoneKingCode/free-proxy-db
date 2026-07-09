"""
FreeProxyDB SDK smoke tests.

Run from `sdk/` directory:
    python test.py

Optional env:
    FREEPROXYDB_API_KEY  — enable UserClient / valid_proxies tests
"""

from __future__ import annotations

import os
import sys

from freeproxydb import ProxyHttpClient, PublicClient, UserClient
from freeproxydb._web_crawler import build_web_crawler_params
from freeproxydb.proxy_pool import ProxyPool
from freeproxydb.proxy_url import (
    https_filter_for_url,
    is_http_proxy_url,
    is_socks_proxy_url,
    proxy_key,
    proxy_url_from_record,
)

API_KEY = os.environ.get("FREEPROXYDB_API_KEY", "").strip()
HTTPBIN = "https://httpbin.org/ip"


def run(name: str, fn) -> bool:
    print(f"\n--- {name} ---")
    try:
        fn()
        print(f"[OK] {name}")
        return True
    except Exception as exc:
        print(f"[FAIL] {name}: {exc}")
        return False


# ---------------------------------------------------------------------------
# PublicClient
# ---------------------------------------------------------------------------


def test_public_statistics():
    with PublicClient() as client:
        stats = client.statistics()
        print("statistics keys:", list(stats.keys())[:5])
        assert isinstance(stats, dict)


def test_public_total_statistics():
    with PublicClient() as client:
        stats = client.total_statistics()
        print("total_statistics keys:", list(stats.keys())[:5])
        assert isinstance(stats, dict)


def test_public_client_ip():
    with PublicClient() as client:
        data = client.client_ip()
        print("client_ip:", data)
        assert data


def test_public_anon_check():
    with PublicClient() as client:
        data = client.anon_check()
        print("anon_check keys:", list(data.keys())[:5])
        assert isinstance(data, dict)


def test_public_search():
    with PublicClient() as client:
        page = client.search(
            protocol=["http", "socks5"],
            page_index=1,
            page_size=5,
            order_by="check_success_count",
            order_dir="desc",
        )
        total = page.get("total_count", 0)
        rows = page.get("data") or []
        print(f"search total={total}, returned={len(rows)}")
        if rows:
            print("first proxy:", proxy_key(rows[0]))
        assert isinstance(page, dict)


def test_public_ip_checker():
    with PublicClient() as client:
        data = client.ip_checker("8.8.8.8")
        print("ip_checker country:", data.get("country") or data.get("country_name"))
        assert isinstance(data, dict)


def test_public_port_checker():
    with PublicClient() as client:
        data = client.port_checker("8.8.8.8", [53, 443], timeout=5)
        print("port_checker:", data)
        assert isinstance(data, dict)


def test_public_subscribe():
    with PublicClient() as client:
        text = client.subscribe(
            protocol="http",
            count=10,
            subscribe_format="original",
        )
        lines = [line for line in text.strip().splitlines() if line.strip()]
        print(f"subscribe lines={len(lines)}, sample={lines[:1]}")
        assert isinstance(text, str)
        assert len(lines) > 0


def test_public_web_crawler():
    with PublicClient() as client:
        try:
            body = client.web_crawler(HTTPBIN, "auto", timeout=15)
        except Exception as exc:
            print(f"web_crawler skipped (auto): {exc}")
            try:
                body = client.web_crawler(HTTPBIN, "http", timeout=15)
            except Exception as exc2:
                print(f"web_crawler skipped (http): {exc2}")
                try:
                    body = client.web_crawler(HTTPBIN, "socks", timeout=15)
                except Exception as exc3:
                    print(f"web_crawler skipped (socks): {exc3}")
                    return
        print("web_crawler body preview:", str(body)[:120])
        assert body


def test_public_web_crawler_post():
    with PublicClient() as client:
        try:
            body = client.web_crawler(
                "https://httpbin.org/post",
                "auto",
                timeout=20,
                method="POST",
                headers={"Content-Type": "application/json"},
                body='{"hello":"world"}',
            )
        except Exception as exc:
            print(f"web_crawler POST skipped: {exc}")
            return
        print("web_crawler POST preview:", str(body)[:160])
        assert "hello" in str(body)


def test_web_crawler_param_validation():
    params = build_web_crawler_params(
        "https://example.com",
        "auto",
        method="POST",
        headers={"User-Agent": "test"},
        body="ok",
    )
    assert params["method"] == "POST"
    assert params["protocol"] == "auto"
    assert "headers" in params
    assert params["body"] == "ok"

    try:
        build_web_crawler_params("https://example.com", "auto", method="GET", body="x")
        assert False, "expected ValueError"
    except ValueError as exc:
        print("validation ok:", exc)

    try:
        build_web_crawler_params("https://example.com", "ftp")
        assert False, "expected ValueError"
    except ValueError as exc:
        print("protocol validation ok:", exc)


def test_public_proxy_checker():
    with PublicClient() as client:
        page = client.search(protocol="http", page_size=1)
        rows = (page or {}).get("data") or []
        if not rows:
            print("skip proxy_checker: no http proxy in search")
            return
        proxy_url = proxy_url_from_record(rows[0])
        results = client.proxy_checker([proxy_url], timeout=10)
        print("proxy_checker:", results)
        assert isinstance(results, list)


# ---------------------------------------------------------------------------
# UserClient (requires FREEPROXYDB_API_KEY)
# ---------------------------------------------------------------------------


def test_user_valid_proxies():
    if not API_KEY:
        print("skip: set FREEPROXYDB_API_KEY to run")
        return
    with UserClient(api_key=API_KEY) as client:
        rows = client.valid_proxies(count=3, protocol=["http", "socks5"])
        print(f"valid_proxies count={len(rows)}")
        if rows:
            print("first:", proxy_key(rows[0]))
        assert isinstance(rows, list)


def test_user_subscribe():
    if not API_KEY:
        print("skip: set FREEPROXYDB_API_KEY to run")
        return
    with UserClient(api_key=API_KEY) as client:
        text = client.subscribe(protocol="http", count=10, subscribe_format="original")
        print(f"user subscribe length={len(text)}")
        assert isinstance(text, str)


def test_user_web_crawler():
    if not API_KEY:
        print("skip: set FREEPROXYDB_API_KEY to run")
        return
    with UserClient(api_key=API_KEY) as client:
        body = client.web_crawler(HTTPBIN, "auto", timeout=15)
        print("user web_crawler preview:", str(body)[:120])
        assert body


# ---------------------------------------------------------------------------
# proxy_url helpers
# ---------------------------------------------------------------------------


def test_proxy_url_helpers():
    http_record = {"protocol": "http", "ip": "1.2.3.4", "port": 8080}
    socks_record = {"protocol": "socks5", "ip": "5.6.7.8", "port": 1080}
    connect_record = {"connect_string": "socks5://9.9.9.9:1080"}

    http_url = proxy_url_from_record(http_record)
    socks_url = proxy_url_from_record(socks_record)
    connect_url = proxy_url_from_record(connect_record)

    print("http_url:", http_url)
    print("socks_url:", socks_url)
    print("connect_url:", connect_url)
    print("https_filter:", https_filter_for_url("https://example.com"))

    assert http_url == "http://1.2.3.4:8080"
    assert socks_url == "socks5://5.6.7.8:1080"
    assert connect_url == "socks5://9.9.9.9:1080"
    assert is_http_proxy_url(http_url)
    assert is_socks_proxy_url(socks_url)
    assert https_filter_for_url("https://x.com") is True
    assert https_filter_for_url("http://x.com") is None


# ---------------------------------------------------------------------------
# ProxyPool
# ---------------------------------------------------------------------------


def test_proxy_pool():
    with PublicClient() as api:
        pool = ProxyPool(
            api,
            protocol=["http", "socks5"],
            pool_size=5,
        )
        added = pool.refill(https=True)
        print(f"pool refill added={added}")
        if added == 0:
            print("skip next(): pool empty")
            return
        record = pool.next(https=True)
        print("pool next:", proxy_key(record))
        pool.mark_failed(record)
        pool.reset_failed()
        assert record


# ---------------------------------------------------------------------------
# ProxyHttpClient
# ---------------------------------------------------------------------------


def test_proxy_http_client_get():
    with ProxyHttpClient(
        protocol=["http", "socks5"],
        pool_size=10,
        max_retries=3,
        timeout=20,
    ) as client:
        result = client.get(HTTPBIN)
        print("proxy:", result.proxy_url)
        print("attempts:", result.attempts)
        print("status:", result.response.status_code)
        print("body preview:", result.response.text[:120])
        assert result.response.status_code == 200


def test_proxy_http_client_fetch():
    with ProxyHttpClient(
        protocol=["http", "socks5"], max_retries=3, timeout=20
    ) as client:
        ok, body, msg, proxy = client.fetch(HTTPBIN)
        print("fetch ok:", ok)
        print("fetch msg:", msg)
        print("fetch proxy:", proxy_key(proxy) if proxy else None)
        print("fetch body preview:", (body or "")[:120])
        assert ok is True
        assert body


def test_proxy_http_client_helpers():
    with ProxyHttpClient(
        protocol=["http", "socks5"], max_retries=3, timeout=20
    ) as client:
        text = client.get_text(HTTPBIN)
        data = client.get_json("https://httpbin.org/get")
        print("get_text preview:", text[:120])
        print("get_json keys:", list(data.keys())[:5])
        assert "origin" in text or "origin" in str(data)


def test_proxy_http_client_with_api_key():
    if not API_KEY:
        print("skip: set FREEPROXYDB_API_KEY to run")
        return
    with ProxyHttpClient(
        api_key=API_KEY,
        protocol=["http", "socks5"],
        max_retries=3,
        timeout=20,
    ) as client:
        result = client.get(HTTPBIN)
        print("user pool proxy:", result.proxy_url)
        assert result.response.status_code == 200


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

TESTS = [
    ("proxy_url helpers", test_proxy_url_helpers),
    ("PublicClient.statistics", test_public_statistics),
    ("PublicClient.total_statistics", test_public_total_statistics),
    ("PublicClient.client_ip", test_public_client_ip),
    ("PublicClient.anon_check", test_public_anon_check),
    ("PublicClient.search", test_public_search),
    ("PublicClient.ip_checker", test_public_ip_checker),
    ("PublicClient.port_checker", test_public_port_checker),
    ("PublicClient.subscribe", test_public_subscribe),
    ("PublicClient.web_crawler", test_public_web_crawler),
    ("PublicClient.web_crawler POST", test_public_web_crawler_post),
    ("web_crawler param validation", test_web_crawler_param_validation),
    ("PublicClient.proxy_checker", test_public_proxy_checker),
    ("UserClient.valid_proxies", test_user_valid_proxies),
    ("UserClient.subscribe", test_user_subscribe),
    ("UserClient.web_crawler", test_user_web_crawler),
    ("ProxyPool", test_proxy_pool),
    ("ProxyHttpClient.get", test_proxy_http_client_get),
    ("ProxyHttpClient.fetch", test_proxy_http_client_fetch),
    ("ProxyHttpClient helpers", test_proxy_http_client_helpers),
    ("ProxyHttpClient (api key)", test_proxy_http_client_with_api_key),
]


def main() -> int:
    print("FreeProxyDB SDK smoke tests")
    print("API_KEY:", "set" if API_KEY else "not set (user tests skipped)")

    passed = 0
    failed = 0
    for name, fn in TESTS:
        if run(name, fn):
            passed += 1
        else:
            failed += 1

    print(f"\n=== done: {passed} passed, {failed} failed ===")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
