# Free Proxy DB — Daily-Updated HTTP, SOCKS5, V2Ray, VMess, VLESS, SSR & MTProto Proxies

> **Live database & free tools:** [**freeproxydb.com**](https://freeproxydb.com/)  
> Browse 1000+ verified proxies, filter by country/protocol, export lists, and use free proxy tools — no signup required.

This repository provides **daily-updated sample proxy lists** and pool statistics.  
For the **full database**, advanced filters, free tools, and API access, visit the website above.

---

## Browse on the Website

| Category | Link |
|----------|------|
| **All Proxies** | [freeproxydb.com](https://freeproxydb.com/) |
| **HTTP / HTTPS** | [freeproxydb.com/freeProxy/http](https://freeproxydb.com/freeProxy/http) |
| **SOCKS5** | [freeproxydb.com/freeProxy/socks5](https://freeproxydb.com/freeProxy/socks5) |
| **V2Ray (VMess / VLESS / Trojan)** | [freeproxydb.com/freeProxy/v2ray](https://freeproxydb.com/freeProxy/v2ray) |
| **Shadowsocks (SS)** | [freeproxydb.com/freeProxy/ss](https://freeproxydb.com/freeProxy/ss) |
| **ShadowsocksR (SSR)** | [freeproxydb.com/freeProxy/ssr](https://freeproxydb.com/freeProxy/ssr) |
| **MTProto / Telegram** | [freeproxydb.com/freeProxy/mtproto](https://freeproxydb.com/freeProxy/mtproto) |
| **Statistics Dashboard** | [freeproxydb.com/statistics](https://freeproxydb.com/statistics) |

---

## Free Tools (Website)

- **[Proxy Checker](https://freeproxydb.com/freeTools/proxyChecker)** — Test availability, speed, and reliability
- **[IP Checker](https://freeproxydb.com/freeTools/ipChecker)** — IP geolocation with interactive map
- **[Port Checker](https://freeproxydb.com/freeTools/portChecker)** — Scan open ports and detect services
- **[Web Crawler](https://freeproxydb.com/freeTools/webCrawler)** — Scrape websites with proxy support
- **[Anonymity Checker](https://freeproxydb.com/anonChecker)** — Verify proxy anonymity level

---

## GitHub Sample Lists (Top 100 per Protocol)

These files under [`proxies/`](proxies/) contain the **top 100 verified proxies per protocol** (sorted by reliability and speed).  
The full database with country/protocol filters and real-time updates is on the website.

| Proxy Type | JSON | TXT |
|------------|------|-----|
| **All (top 500)** | [all.json](https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/refs/heads/main/proxies/all.json) | [all.txt](https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/refs/heads/main/proxies/all.txt) |
| **HTTP** | [http.json](https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/refs/heads/main/proxies/http.json) | [http.txt](https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/refs/heads/main/proxies/http.txt) |
| **SOCKS4** | [socks4.json](https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/refs/heads/main/proxies/socks4.json) | [socks4.txt](https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/refs/heads/main/proxies/socks4.txt) |
| **SOCKS5** | [socks5.json](https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/refs/heads/main/proxies/socks5.json) | [socks5.txt](https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/refs/heads/main/proxies/socks5.txt) |
| **V2Ray** | [v2ray.json](https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/refs/heads/main/proxies/v2ray.json) | [v2ray.txt](https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/refs/heads/main/proxies/v2ray.txt) |
| **Shadowsocks (SS)** | [ss.json](https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/refs/heads/main/proxies/ss.json) | [ss.txt](https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/refs/heads/main/proxies/ss.txt) |
| **SSR** | [ssr.json](https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/refs/heads/main/proxies/ssr.json) | [ssr.txt](https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/refs/heads/main/proxies/ssr.txt) |
| **MTProto** | [mtproto.json](https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/refs/heads/main/proxies/mtproto.json) | [mtproto.txt](https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/refs/heads/main/proxies/mtproto.txt) |

### Quick Usage

```bash
# Download top SOCKS5 sample
curl -O https://raw.githubusercontent.com/LoneKingCode/free-proxy-db/main/proxies/socks5.txt
```

---

## Python SDK (`sdk/`)

> **Note:** PyPI package `freeproxydb` is **not published yet**. Install from source below for now.

The [`sdk/`](sdk/) directory contains the official **FreeProxyDB Python SDK**.  
It wraps the public and user REST APIs so you can search proxies, fetch subscription feeds, run checker tools, and send HTTP requests with **automatic HTTP/SOCKS proxy rotation** — no manual proxy list handling required.

The SDK is kept in sync with this repository whenever proxy sample lists are updated.

### Install

```bash
# PyPI (coming soon — not available yet)
# pip install freeproxydb
```

Install from this repo (current method):

```bash
git clone https://github.com/LoneKingCode/free-proxy-db.git
cd free-proxy-db/sdk
pip install -e .
```

### Quick Example

```python
from freeproxydb import PublicClient, ProxyHttpClient

# Search proxies (no API key)
with PublicClient() as client:
    page = client.search(country="US", protocol=["http", "socks5"], page_size=10)
    print(page["total_count"], len(page["data"]))

# HTTP request via auto-rotating HTTP/SOCKS proxies
with ProxyHttpClient(protocol=["http", "socks5"], max_retries=5) as client:
    result = client.get("https://httpbin.org/ip")
    print(result.proxy_url, result.response.text)
```

With an API key you get access to the high-quality pool (`valid_proxies`) and higher subscribe limits. See the full SDK guide in [`sdk/README.md`](sdk/README.md).

---

## GitHub vs Website vs API Key

| Feature | GitHub Sample | Website / Public API | API Key |
|---------|---------------|----------------------|---------|
| Data volume | Top 100 / protocol | Full database | Full database |
| Data quality | Standard verified | Standard verified | High-quality pool |
| Filters | None | Country, protocol, link type | Country, protocol, link type |
| Rate limits | None (static files) | Yes | Higher quotas |
| Free tools | No | Yes | Yes |
| Real-time updates | Periodic sync | Real-time | Real-time |

Need higher quotas, faster proxies, or programmatic access at scale?  
Request an **API Key** via Telegram on [freeproxydb.com](https://freeproxydb.com/) (see [API Documentation](https://freeproxydb.com/documentation/apiDocs)).

---

## Developer Resources

- **[API Documentation](https://freeproxydb.com/documentation/apiDocs)** — REST API reference
- **[Python SDK](sdk/README.md)** — install from `sdk/` (PyPI coming soon), full examples and API coverage
- **[Code Examples](https://freeproxydb.com/documentation/codeUsage)** — Python, Java, PHP integration
- **[Web Crawler Guide](https://freeproxydb.com/documentation/webCrawlerDocs)** — Scraping best practices
- **[FAQ](https://freeproxydb.com/documentation/faq)** — Common questions

### Public API (No Key Required, Rate-Limited)

```
GET https://freeproxydb.com/api/proxy/search?protocol=socks5&page_size=20
GET https://freeproxydb.com/api/proxy/subscribe?protocol=v2ray&count=50
```

### API Key Endpoints (High-Quality Pool)

```
GET https://freeproxydb.com/api/user/valid_proxies?count=100
GET https://freeproxydb.com/api/user/subscribe?protocol=mtproto&count=200
```

See [API Documentation](https://freeproxydb.com/documentation/apiDocs) for authentication and limits.

---

## Repository Layout

```
free-proxy-db/
├── proxies/          # Daily-updated sample lists (JSON + TXT)
├── sdk/              # Official Python SDK (PyPI: freeproxydb — coming soon)
│   ├── freeproxydb/
│   └── README.md     # Full SDK documentation
└── README.md
```

---

## Supported Protocols

HTTP · HTTPS · SOCKS4 · SOCKS5 · V2Ray · VMess · VLESS · Trojan · Shadowsocks (SS) · ShadowsocksR (SSR) · MTProto · Telegram (`tg://`)

---

## Why Free Proxy DB?

- **1000+ daily-verified proxies** across multiple protocols
- **Real-time validation** with success count and speed metrics
- **Global coverage** — filter by country and protocol
- **No registration** for website browsing and public tools
- **Export support** — JSON, TXT, CSV
- **Developer-friendly** — REST API, Python SDK, code examples, GitHub samples

---

*Free Proxy DB — [freeproxydb.com](https://freeproxydb.com/)*
