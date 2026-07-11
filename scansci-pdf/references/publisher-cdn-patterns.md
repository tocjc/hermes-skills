# Publisher CDN / Direct-Download URL Patterns

When the main publisher website is blocked by CDN protection (Akamai, Cloudflare, etc.), 
many open-access publishers serve PDFs from separate CDN domains that are less restrictive.

## MDPI (mdpi-res.com)

**Main site:** `www.mdpi.com` — protected by Akamai Bot Manager (HTTP 403 for curl/browserless)

**CDN domain:** `mdpi-res.com`

**URL pattern:**
```
https://mdpi-res.com/d_attachment/{journal}/{journal-abbrev}-{article-id}/article_deploy/{journal-abbrev}-{article-id}.pdf
```

**Example (Sensors, article 2967, volume 25, issue 10):**
```
https://mdpi-res.com/d_attachment/sensors/sensors-25-02967/article_deploy/sensors-25-02967.pdf
```

**How to construct:**
- `{journal}` = the journal slug (e.g., `sensors`, `remotesensing`, `applsci`, `energies`)
- `{journal-abbrev}` = the abbreviated journal name used in filenames (e.g., `sensors`)
- `{article-id}` = the article number from the URL (e.g., from `/1424-8220/25/10/2967` → `25-02967`)

**Finding the article ID:**
From the article URL `https://www.mdpi.com/1424-8220/{volume}/{issue}/{article}`:
- The article ID is the last segment before any suffix
- The filename pattern is `{journal-abbrev}-{volume}-0{article}` (zero-padded to 5 digits)

**Alternative: notes page**
The article notes page (`https://www.mdpi.com/1424-8220/25/10/2967/notes`) contains the upload timestamp 
which can be used as a version parameter: `/pdf?version={timestamp}`

## PubMed Central (PMC)

**Main site:** `pmc.ncbi.nlm.nih.gov` — protected by Google reCAPTCHA for automated downloads

**PDF URL pattern (when accessible):**
```
https://pmc.ncbi.nlm.nih.gov/articles/PMC{pmcid}/pdf/{filename}.pdf
```

**Note:** PMC requires reCAPTCHA verification for all non-browser requests as of 2025. 
Not suitable for automated download without a browser session. Prefer the publisher's own 
CDN or direct PDF link.

## Nature (nature.com)

**Main site:** `www.nature.com` — generally accessible to curl

**PDF URL pattern:**
```
https://www.nature.com/articles/{article-id}.pdf
```

**Example:**
```
https://www.nature.com/articles/s41598-025-99346-5.pdf
```

No special headers or cookies needed. Works with standard curl.

## IEEE (ieeexplore.ieee.org)

**Search API (no auth needed):**
```
POST https://ieeexplore.ieee.org/rest/search
Content-Type: application/json
Referer: https://ieeexplore.ieee.org/
Origin: https://ieeexplore.ieee.org

{"queryText":"YOUR_QUERY","pageNumber":1,"rowsPerPage":10,"returnFacets":["ALL"]}
```

## General approach for CDN-blocked publishers

1. Try `www.{publisher}.com/{article-path}/pdf` with standard curl
2. If blocked (HTTP 403/503), search for the publisher's CDN domain:
   - MDPI: `mdpi-res.com`
   - Elsevier: `pdf.sciencedirectassets.com`
   - Springer: `link.springer.com/content/pdf/` (works directly)
3. If the publisher hosts on PubMed Central, check if the article is there
4. As last resort, use Semantic Scholar or Unpaywall API to find OA PDF URLs
5. ResearchGate and Academia.edu may also host author versions