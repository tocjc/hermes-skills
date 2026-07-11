# Hard-to-Find Papers — Search Strategy Guide

When a paper does not turn up in the first round of database searches (CrossRef, Semantic Scholar, OpenAlex, arXiv), follow this escalation path instead of grinding on one channel.

## Tier 1: Direct Academic APIs (Parallel)

Run these independently in the same turn — they do not depend on each other:

| Source | Tool | Notes |
|--------|------|-------|
| **CrossRef** | `curl -s "https://api.crossref.org/works?query.title=..."` | Best coverage for published journal articles. Filter by ISSN for venue-specific search. |
| **OpenAlex** | `curl -s "https://api.openalex.org/works?search=..."` | Free, no key. Supports `filter=publication_year:2024`. |
| **Semantic Scholar** | `sn-search-academic` script or direct `curl` | Rate-limited (429) from cloud IPs. Try `sleep 3` between requests. |
| **arXiv** | `sn-search-academic/scripts/arxiv_search.py` | Only preprints, but has `journal_ref` field linking to published DOI. |

**Important**: run these as parallel tool calls or via `delegate_task` — not sequentially. Serial execution wastes rounds when all 4 could complete in one turn.

## Tier 2: Free Web Search (Fallback)

If Tier 1 returns nothing, do NOT try heavy browser-based searches first. Use lightweight HTTP calls:

| Source | Method | Reliability on cloud IPs |
|--------|--------|------------------------|
| **DuckDuckGo Instant Answer API** | `curl -s "https://api.duckduckgo.com/?q=...&format=json"` | Low — only returns Instant Answers, not organic results |
| **Baidu (stealth)** | `baidu-stealth-search.js` script | Mixed — good for Chinese content, poor for specific English academic titles |
| **Bing / Google / Google Scholar** | Browser only | **Blocked from cloud/VPS IPs** — CAPTCHA or 418 errors. Do not waste time. |

## Tier 3: When All Databases Return Nothing

At this point, the paper likely falls into one of these buckets:

### A. Early Access (Not Yet Indexed)
- IEEE Early Access articles take **weeks to months** to appear in CrossRef/OpenAlex
- The DOI may exist but not be resolvable yet
- **Action**: ask user for **IEEE article number** (8-digit number from the URL) or the DOI directly
- Once you have the DOI, use `mcp_scansci_pdf_smart_download` — it can handle Early Access papers through Sci-Hub/LibGen fallback chains

### B. Title Mismatch
- The user's title may be slightly different from the publisher's record
- **Action**: ask user for the full author list (Chinese name helps) or any link where they saw the paper

### C. Wrong Venue or Year
- The paper may be in a different journal (e.g., IEEE TII, MSSP, Mechanical Systems and Signal Processing) or a different year
- **Action**: search broader — drop the venue constraint, search by title across all years

## Signal: When to Ask the User Directly

Do not exhaustively search every channel before asking. **Ask after Tier 1 + 1 attempt at Tier 2 returns nothing.** Specifically ask for:

1. **DOI** (most useful — enables smart_download immediately)
2. **IEEE article number** (e.g., 11036832 — from ieeexplore.ieee.org/document/NUMBER/)
3. **Full author names** (particularly the Chinese name for Chen/Zhang/Wang papers)
4. **Any link** (ResearchGate, Google Scholar, institutional repository)

## Known Cloud-IP Pitfalls

These platforms will **consistently** block or CAPTCHA requests from cloud/VPS IP addresses:

| Platform | Block Pattern | Workaround |
|----------|---------------|------------|
| Google Scholar | "Sorry..." page | None from cloud IP |
| IEEE Xplore | HTTP 418 "Unusual Traffic" | None from cloud IP |
| Bing | CAPTCHA challenge | None for programmatic access |
| ResearchGate | Cloudflare Access Denied (1020) | None from cloud IP |
| Startpage | CAPTCHA | None from cloud IP |
| DuckDuckGo HTML | CAPTCHA iframe | Try `api.duckduckgo.com` (Instant Answer only) |

**Do not attempt browser-based searches on these from cloud IPs** — you will waste rounds on CAPTCHA resolution that cannot be automated.

## Recommended Search Order (Minimizes Wasted Attempts)

```
1. CrossRef (best single source for published articles)         ← parallel
   OpenAlex (backup / broader coverage)                         ←
   arXiv (for preprints with journal_ref)                       ←

2. If DOI found → smart_download
   If no DOI found → ask user for: DOI, article number, or link
                     OR try Tier 2 lightweight searches

3. If user provides IEEE article number or DOI → smart_download
   If user provides author names → retry CrossRef/OpenAlex with author filter

4. If still nothing → report: "Paper not found in any index.
   Likely Early Access or title mismatch. Cannot proceed without a DOI or link."
```