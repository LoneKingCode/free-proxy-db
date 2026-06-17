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

### Browse by Link Type (Subscription URLs)

| Link Type | Website |
|-----------|---------|
| VMess (`vmess://`) | [freeproxydb.com/freeProxy/linktype/vmess](https://freeproxydb.com/freeProxy/linktype/vmess) |
| VLESS (`vless://`) | [freeproxydb.com/freeProxy/linktype/vless](https://freeproxydb.com/freeProxy/linktype/vless) |
| Trojan (`trojan://`) | [freeproxydb.com/freeProxy/linktype/trojan](https://freeproxydb.com/freeProxy/linktype/trojan) |
| Shadowsocks (`ss://`) | [freeproxydb.com/freeProxy/linktype/ss](https://freeproxydb.com/freeProxy/linktype/ss) |
| SSR (`ssr://`) | [freeproxydb.com/freeProxy/linktype/ssr](https://freeproxydb.com/freeProxy/linktype/ssr) |
| Telegram (`tg://`) | [freeproxydb.com/freeProxy/linktype/tg](https://freeproxydb.com/freeProxy/linktype/tg) |

---

## Free Tools (Website)

- **[Proxy Checker](https://freeproxydb.com/freeTools/proxyChecker)** — Test availability, speed, and reliability
- **[IP Checker](https://freeproxydb.com/freeTools/ipChecker)** — IP geolocation with interactive map
- **[Port Checker](https://freeproxydb.com/freeTools/portChecker)** — Scan open ports and detect services
- **[Web Crawler](https://freeproxydb.com/freeTools/webCrawler)** — Scrape websites with proxy support
- **[Anonymity Checker](https://freeproxydb.com/anonChecker)** — Verify proxy anonymity level

---

## GitHub Sample Lists (Top 100 per Protocol)

These files contain the **top 100 verified proxies per protocol** (sorted by reliability and speed).  
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

## GitHub vs Website vs API Key

| Feature | GitHub Sample | Website / Public API |
|---------|---------------|----------------------|
| Data volume | Top 100 / protocol | Full database |
| Data quality | Standard verified | Standard verified |
| Filters | None | Country, protocol, link type |
| Rate limits | None (static files) | Yes |
| Free tools | No | Yes | Yes |
| Real-time updates | Periodic sync | Real-time |

Need higher quotas, faster proxies, or programmatic access at scale?  
Request an **API Key** via Telegram on [freeproxydb.com](https://freeproxydb.com/) (see [API Documentation](https://freeproxydb.com/documentation/apiDocs)).

---

## Developer Resources

- **[API Documentation](https://freeproxydb.com/documentation/apiDocs)** — REST API reference
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

## Supported Protocols

HTTP · HTTPS · SOCKS4 · SOCKS5 · V2Ray · VMess · VLESS · Trojan · Shadowsocks (SS) · ShadowsocksR (SSR) · MTProto · Telegram (`tg://`)

---

## Why Free Proxy DB?

- **1000+ daily-verified proxies** across multiple protocols
- **Real-time validation** with success count and speed metrics
- **Global coverage** — filter by country and protocol
- **No registration** for website browsing and public tools
- **Export support** — JSON, TXT, CSV
- **Developer-friendly** — REST API, code examples, GitHub samples

---

*Free Proxy DB — [freeproxydb.com](https://freeproxydb.com/)*
