# Search Fallback Strategies for Network-Constrained Environments

> Discovered: 2026-06-05  
> Context: SDU professor research failed on Bing, Baidu, Semantic Scholar, Chinese social platforms

## When Standard Search Engines Fail

### Observed Failure Modes

| Tool | Failure Mode | Root Cause |
|------|-------------|------------|
| **Baidu** (curl) | CAPTCHA block (百度安全验证) | Server-side bot detection on raw curl requests |
| **Bing** (curl) | Returns garbage results (unrelated English content) for Chinese queries | Server-side language detection; treats Chinese query as byte-level token |
| **Semantic Scholar API** | HTTP 429 "Too Many Requests" | Rate limiting from shared IP |
| **Google Scholar** (curl) | CAPTCHA/blank response | Bot detection |
| **Git clone** (GitHub) | `GnuTLS recv error` / timeout | TLS handshake failure on some networks; proxy misconfiguration |
| **Browser** (Camofox) | "Cannot connect to Camofox" | Browser service not running in environment |

### What Usually Works

1. **Official university/company websites** via curl — Most Chinese institutional sites (`.edu.cn`, `.gov.cn`) respond to plain curl with proper User-Agent
2. **raw.githubusercontent.com** — TLS works, no proxy needed, even when `github.com` itself doesn't
3. **GitHub API** (`api.github.com/git/trees/...?recursive=1`) — Works for getting repo structure
4. **Wikipedia API** — Sometimes works, but `zh.wikipedia.org` may also fail; `en.wikipedia.org` is more reliable
5. **Direct URL access** — If you know the exact URL (from previous search results), `curl -sL` to that URL directly often works even when search fails

## Strategy: Start with the Known Target

When searching for a specific Chinese person/institution, and search engines fail:

1. **Direct URL hypothesis**: Try to guess the official profile URL pattern
   - SDU School of Literature faculty: `https://www.lit.sdu.edu.cn/info/1133/1582.htm` (pattern: `/info/{category}/{id}.htm`)
   - Most `.edu.cn` sites use CMS with predictable URL patterns

2. **Bing fallback**: Use English query terms when Chinese queries fail
   - "Liu Zuguo Shandong University" may return better results than Chinese
   - Add the English institution name: `"liu zuguo" "shandong university"`

3. **Semantic Scholar with delays**: If 429'd, wait 30+ seconds before retrying
   - Use the Author search endpoint instead of Paper search to reduce contention

4. **Primary source > aggregation**: Once you get ANY link (even from garbage search results), extract the legitimate URL and access it directly

## Key URLs for Chinese Academic Research

### Shandong University
- School of Literature: `https://www.lit.sdu.edu.cn/`
- Faculty directory index: `https://www.lit.sdu.edu.cn/szdw/jsml.htm`

### Other useful direct URLs
- Baidu Baike (encyclopedia): `https://baike.baidu.com/`
- CNKI (知网): `https://www.cnki.net/` (requires login for full text)
