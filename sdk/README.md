# FreeProxyDB Python SDK

[![PyPI version](https://img.shields.io/pypi/v/freeproxydb.svg)](https://pypi.org/project/freeproxydb/)
[![Python](https://img.shields.io/pypi/pyversions/freeproxydb.svg)](https://pypi.org/project/freeproxydb/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Official Python client for the [FreeProxyDB](https://freeproxydb.com) proxy pool API.

Search proxies, fetch subscription feeds, run built-in checker tools, and make HTTP requests with **automatic HTTP/SOCKS proxy rotation** — all from a typed, `httpx`-based SDK.

- **Website:** [freeproxydb.com](https://freeproxydb.com)
- **API documentation:** [freeproxydb.com/documentation/apiDocs](https://freeproxydb.com/documentation/apiDocs)
- **Repository:** [github.com/LoneKingCode/free-proxy-db](https://github.com/LoneKingCode/free-proxy-db) (`sdk/` directory)

## Features

- **Public API** — search, subscribe, statistics, IP/port/proxy checkers, web crawler (no API key)
- **User API** — high-quality `valid_proxies`, higher subscribe limits, authenticated web crawler (API key)
- **`ProxyHttpClient`** — route outbound HTTP through the pool with automatic failover (HTTP / SOCKS4 / SOCKS5)
- **Typed & lightweight** — Python 3.9+, single runtime dependency: `httpx[socks]`
- **Context managers** — all clients support `with ... as client:` for clean resource handling

## Requirements

- Python **3.9+**
- Network access to `https://freeproxydb.com/api` (or your self-hosted instance)

## Install

From PyPI:

```bash
pip install freeproxydb
```

From source:

```bash
git clone https://github.com/LoneKingCode/free-proxy-db.git
cd free-proxy-db/sdk
pip install -e .
```

With dev dependencies (for running smoke tests):

```bash
pip install -e ".[dev]"
```

## Quick start

### Public API (no API key)

```python
from freeproxydb import PublicClient

with PublicClient() as client:
    # Paginated search
    page = client.search(
        country="US",
        protocol=["http", "socks5"],
        page_size=10,
        order_by="check_success_count",
        order_dir="desc",
    )
    print(page["total_count"], len(page["data"]))

    # Subscription feed (plain text or base64 v2ray format)
    feed = client.subscribe(country="US", count=50, subscribe_format="v2ray")

    # Pool statistics
    stats = client.statistics()

    # Checker tools
    ip_info = client.ip_checker("8.8.8.8")
    port_result = client.port_checker("8.8.8.8", [80, 443], timeout=5)
    check_results = client.proxy_checker(
        ["http://1.2.3.4:8080", "socks5://1.2.3.4:1080"],
        timeout=20,
    )
```

Filter parameters (`country`, `protocol`, `anonymity`, …) accept a comma-separated string or a list of strings.

### User API (API key required)

Register at [freeproxydb.com](https://freeproxydb.com) to obtain an API key, then:

```python
from freeproxydb import UserClient

with UserClient(api_key="YOUR_API_KEY") as user:
    # Top validated proxies
    proxies = user.valid_proxies(
        count=20,
        country="US",
        protocol=["http", "socks5"],
        simple=True,
    )

    # Authenticated subscription (higher limits)
    feed = user.subscribe(count=100, subscribe_format="original")

    # Server-side fetch through a proxy (recommended: protocol="auto")
    body = user.web_crawler("https://example.com", protocol="auto", timeout=30)
```

You can pass the key from an environment variable:

```python
import os
from freeproxydb import UserClient

user = UserClient(api_key=os.environ["FREEPROXYDB_API_KEY"])
```

The SDK sends the key via the `X-API-KEY` header (recommended). The server also accepts `api_key` as a query parameter.

### Web Crawler (server-side fetch)

Both `PublicClient.web_crawler` and `UserClient.web_crawler` call FreeProxyDB’s server-side crawler. You send a target URL; the API routes the request through HTTP, SOCKS, and/or the internal **Xray pool** (VMess, VLESS, Trojan, etc.) and returns the **response body text**.

| | Public | User (API key) |
|---|--------|----------------|
| Route | `GET /proxy/web_crawler` | `GET /user/web_crawler` |
| Limits | Per client IP | Per API key (higher quotas) |
| Pool | Validated public pool | High-quality pool + Xray |

**Protocol modes**

| Value | Behavior |
|-------|----------|
| `http` | Random HTTP proxy from the validated pool |
| `socks` | SOCKS pool; may use Xray share-link nodes |
| `auto` | Full routing with automatic retries (**recommended**) |

**Basic GET**

```python
from freeproxydb import PublicClient

with PublicClient() as client:
    html = client.web_crawler(
        "https://httpbin.org/get",
        protocol="auto",
        timeout=30,
    )
    print(html[:200])
```

**POST with custom headers, cookie, and body**

```python
from freeproxydb import PublicClient, UserClient

payload = '{"hello":"world"}'
headers = {
    "Content-Type": "application/json",
    "User-Agent": "MyBot/1.0",
}

with PublicClient() as client:
    body = client.web_crawler(
        "https://httpbin.org/post",
        protocol="auto",
        method="POST",
        headers=headers,
        cookie="session=abc123",
        body=payload,
        timeout=30,
    )

# headers may also be a JSON string (same as the REST API)
with UserClient(api_key="YOUR_API_KEY") as user:
    body = user.web_crawler(
        "https://httpbin.org/post",
        protocol="auto",
        method="POST",
        headers='{"Content-Type":"application/json"}',
        body=payload,
    )
```

**Parameter reference**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `url` | Yes | Full target URL |
| `protocol` | Yes | `http`, `socks`, or `auto` |
| `timeout` | No | 1–60 seconds |
| `method` | No | `GET` (default) or `POST` |
| `headers` | No | `dict[str, str]` or JSON object string (max 30 entries) |
| `cookie` | No | Shorthand for the `Cookie` header |
| `body` | No | Raw POST body; only allowed with `method="POST"` |

Hop-by-hop headers such as `Host` and `Content-Length` are rejected. Invalid combinations (e.g. `body` with `GET`) raise `ValueError` locally before the HTTP call.

For production scrapers and integrations, prefer `UserClient.web_crawler` with `protocol="auto"`.

### Proxied HTTP requests (auto switch HTTP/SOCKS)

`ProxyHttpClient` pulls proxies from the API, tries them in order, and skips failures automatically.

```python
from freeproxydb import ProxyHttpClient

# Public pool (search API)
with ProxyHttpClient(
    country="US",
    protocol=["http", "socks5", "socks4"],
    pool_size=20,
    max_retries=5,
    timeout=30,
) as client:
    result = client.get("https://httpbin.org/ip")
    print(result.proxy_url)          # e.g. socks5://1.2.3.4:1080
    print(result.attempts)           # how many proxies were tried
    print(result.response.status_code)
    print(result.response.text)

    # Convenience helpers
    text = client.get_text("https://httpbin.org/ip")
    data = client.get_json("https://httpbin.org/get")

# High-quality pool (API key → valid_proxies)
with ProxyHttpClient(api_key="YOUR_API_KEY", protocol=["http", "socks5"]) as client:
    ok, body, msg, proxy = client.fetch("https://example.com")
    print(ok, msg, proxy)
```

**`ProxyHttpClient` options**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `api_key` | `None` | If set, uses `valid_proxies`; otherwise uses public `search` |
| `base_url` | `https://freeproxydb.com/api` | API base URL |
| `country` | `""` | Country filter passed to the API |
| `protocol` | `"http,socks5,socks4"` | Protocol filter |
| `pool_size` | `20` | Proxies fetched per refill (max 100) |
| `max_retries` | `5` | Max proxy attempts per request |
| `timeout` | `30.0` | Request timeout (seconds) |
| `verify` | `False` | TLS certificate verification for target URLs |
| `follow_redirects` | `True` | Follow HTTP redirects |

When the target URL is `https://...`, the client automatically requests proxies that support HTTPS tunneling.

Only classic **HTTP / SOCKS4 / SOCKS5** proxies are supported in `ProxyHttpClient`. Xray/V2Ray share links are not handled here (use `subscribe` or server-side `web_crawler` instead).

### Custom base URL (self-hosted)

```python
from freeproxydb import PublicClient, UserClient

client = PublicClient(base_url="http://127.0.0.1:8000/api")
user = UserClient(api_key="...", base_url="http://127.0.0.1:8000/api")
```

## Error handling

All API errors inherit from `FreeProxyDBError`. HTTP status and server `detail` are attached when available.

```python
from freeproxydb import (
    PublicClient,
    ProxyHttpClient,
    ApiError,
    RateLimitError,
    ProxyRequestError,
    ProxyPoolExhaustedError,
)

client = PublicClient()
try:
    client.search(page_size=100)
except RateLimitError as exc:
    print(exc.status_code, exc.detail)
except ApiError as exc:
    print("API error:", exc)

proxy_client = ProxyHttpClient(max_retries=3)
try:
    proxy_client.get("https://example.com")
except ProxyRequestError as exc:
    print("All proxies failed:", exc)
except ProxyPoolExhaustedError as exc:
    print("Pool empty:", exc)
finally:
    proxy_client.close()
```

| Exception | Typical cause |
|-----------|----------------|
| `AuthenticationError` | Missing or invalid API key (401) |
| `AuthorizationError` | Key disabled, expired, or IP not allowed (403) |
| `RateLimitError` | Rate limit or quota exceeded (429) |
| `ApiError` | Other HTTP / API envelope errors |
| `ProxyRequestError` | All proxy attempts failed for one URL |
| `ProxyPoolExhaustedError` | API returned no usable proxies |

## API coverage

| SDK method | HTTP route | Auth |
|------------|------------|------|
| `PublicClient.search` | `GET /proxy/search` | No |
| `PublicClient.subscribe` | `GET /proxy/subscribe` | No |
| `PublicClient.statistics` | `GET /proxy/statistics` | No |
| `PublicClient.total_statistics` | `GET /proxy/total_statistics` | No |
| `PublicClient.client_ip` | `GET /proxy/client_ip` | No |
| `PublicClient.anon_check` | `GET /proxy/anon_check` | No |
| `PublicClient.web_crawler` | `GET /proxy/web_crawler` | No — supports `method`, `headers`, `cookie`, `body` |
| `PublicClient.proxy_checker` | `POST /proxy/proxy_checker` | No |
| `PublicClient.ip_checker` | `GET /proxy/ip_checker` | No |
| `PublicClient.port_checker` | `GET /proxy/port_checker` | No |
| `UserClient.valid_proxies` | `GET /user/valid_proxies` | API key |
| `UserClient.subscribe` | `GET /user/subscribe` | API key |
| `UserClient.web_crawler` | `GET /user/web_crawler` | API key — same advanced options as public |

**HTTP client helpers (local, not REST endpoints)**

| Class | Purpose |
|-------|---------|
| `ProxyHttpClient` | HTTP requests via rotating proxies |
| `ProxyPool` | Lower-level proxy queue from API |
| `proxy_url_from_record` | Build `http://` / `socks5://` URL from API record |

Admin endpoints are intentionally excluded from this SDK.

## Testing

A live smoke-test script is included. It calls the public API and (optionally) user endpoints against production:

```bash
cd sdk
pip install -e ".[dev]"
python test.py
```

To include User API / `valid_proxies` tests:

```bash
# Linux / macOS
export FREEPROXYDB_API_KEY=your_key
python test.py

# Windows PowerShell
$env:FREEPROXYDB_API_KEY = "your_key"
python test.py
```

## Project layout

```
free-proxy-db/               # public proxy list repository
├── http/                    # sample proxy lists (from push_github.py)
├── socks5/
├── all/
├── sdk/                     # Python SDK (this package)
│   ├── freeproxydb/
│   ├── test.py
│   ├── pyproject.toml
│   ├── LICENSE
│   ├── publish.sh
│   ├── publish.ps1
│   └── README.md
└── README.md
```

## Publishing to PyPI (maintainers)

Set [PyPI API token](https://pypi.org/manage/account/token/) credentials:

```bash
# Linux / macOS
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-AgEI...

# Windows PowerShell
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "pypi-AgEI..."
```

One-click publish from `sdk/`:

```bash
cd sdk
# Linux / macOS
chmod +x publish.sh
./publish.sh              # PyPI
./publish.sh --test       # TestPyPI
./publish.sh --dry-run    # build only
```

```powershell
# Windows
.\publish.ps1             # PyPI
.\publish.ps1 -Test       # TestPyPI
.\publish.ps1 -DryRun     # build only

# or
publish.bat -DryRun -Yes
```

Manual equivalent:

```bash
cd sdk
pip install build twine
python -m build
twine upload dist/*
```

Bump `version` in `pyproject.toml` and `freeproxydb/__init__.py` before each release.

For CI in the `free-proxy-db` repository, copy `ci/sdk-test.yml` to `.github/workflows/sdk-test.yml` at the repo root.

## License

MIT — see [LICENSE](LICENSE).

## Links

- [FreeProxyDB](https://freeproxydb.com)
- [API documentation](https://freeproxydb.com/documentation/apiDocs)
- [GitHub repository](https://github.com/LoneKingCode/free-proxy-db)
- [PyPI package](https://pypi.org/project/freeproxydb/)
