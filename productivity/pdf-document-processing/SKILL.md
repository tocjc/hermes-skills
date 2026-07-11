---
name: pdf-document-processing
description: Complete PDF and document processing — generate Chinese PDFs from Markdown (pandoc+xelatex), edit PDF text with nano-pdf, and extract text from PDFs/scans (pymupdf/marker-pdf).
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [pdf, document, cjk, chinese, pandoc, ocr, extraction, editing]
    related_skills: [powerpoint, excel-author, pptx-author]
---

# PDF & Document Processing

Three complementary document workflows: **generate** Chinese PDFs from Markdown, **edit** existing PDF text, and **extract** text from PDFs/scans.

---

## Section A: Chinese PDF Generation (Markdown → PDF)

Generate PDFs from Markdown with correctly embedded CJK fonts. The only reliable toolchain: **pandoc + xelatex**.

### Truth

**weasyPrint does NOT embed CJK fonts.** A PDF generated via weasyPrint from Chinese Markdown renders garbled on any system without the same Chinese fonts installed. This is a weasyPrint design limitation, not a config issue.

### Prerequisites

```bash
apt-get install -y texlive-xetex texlive-lang-chinese fonts-noto-cjk
```

### Command

```bash
pandoc report.md \
  --pdf-engine=xelatex \
  -V mainfont="Noto Sans CJK SC" \
  -V CJKmainfont="Noto Sans CJK SC" \
  -V geometry:margin=2.5cm \
  -o report.pdf
```

### Options Explained

| Option | Value | Purpose |
|--------|-------|---------|
| `--pdf-engine` | `xelatex` | Use XeLaTeX (supports Unicode + system fonts) |
| `-V mainfont` | `Noto Sans CJK SC` | Default font (Latin + CJK) |
| `-V CJKmainfont` | `Noto Sans CJK SC` | Explicit CJK font (required for Chinese) |
| `-V geometry` | `margin=2.5cm` | Page margins |

### Font Embedding Verification

```bash
python3 -c "data = open('report.pdf', 'rb').read(); print(f'CIDFontType0C occurrences: {data.count(b\"CIDFontType0C\")}')"
# ≥2 means CJK fonts are embedded as CID fonts
```

### What NOT to Use

| Tool | Why it fails |
|------|-------------|
| weasyPrint | Does not embed CJK fonts |
| wkhtmltopdf 0.12.6 | No CSS @font-face for CJK |
| fpdf / reportlab | Manual font handling, over-engineered for Markdown→PDF |

### Pitfalls

- **weasyPrint: never use for Chinese** — generates valid PDF that renders blank/garbled
- **Always set both `mainfont` and `CJKmainfont`** — otherwise font mismatch
- **Missing Noto Sans CJK SC** → xelatex falls back to Computer Modern. Install `fonts-noto-cjk`
- **Mermaid diagrams** — xelatex doesn't render them. Convert to ASCII art or static images first
- **Long code lines overflow** — fold manually or use `fold -s -w 80`

See `references/chinese-pdf-generation.md` for full usage examples.

---

## Section B: PDF Text Editing (nano-pdf)

Edit PDFs using natural-language instructions via the nano-pdf CLI.

### Prerequisites

```bash
uv pip install nano-pdf
```

### Usage

```bash
nano-pdf edit <file.pdf> <page_number> "<instruction>"
```

### Examples

```bash
# Change a title on page 1
nano-pdf edit deck.pdf 1 "Change the title to 'Q3 Results' and fix the typo"

# Fix content
nano-pdf edit contract.pdf 2 "Change the client name from 'Acme Corp' to 'Acme Industries'"
```

### Notes

- Page numbers may be 0-based or 1-based depending on version — if the edit hits the wrong page, retry with ±1
- Always verify the output PDF after editing
- Works well for text changes; complex layout modifications may need a different approach

---

## Section C: PDF & Document Extraction

For DOCX: use `python-docx`. For PPTX: see the `powerpoint` skill. This section covers **PDFs and scanned documents**.

### Step 1: Remote URL Available?

If the document has a URL, always try `web_extract` first:
```python
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
```

### Step 2: Choose Local Extractor

| Feature | pymupdf (~25MB) | marker-pdf (~3-5GB) |
|---------|-----------------|---------------------|
| Text-based PDF | ✅ | ✅ |
| Scanned PDF (OCR) | ❌ | ✅ |
| Tables | ✅ (basic) | ✅ (high accuracy) |
| Equations | ❌ | ✅ |
| Install size | ~25MB | ~3-5GB |
| Speed | Instant | ~1-14s/page (CPU) |

**Decision**: Use pymupdf unless you need OCR, equations, or complex layout.

### pymupdf (lightweight)

```bash
pip install pymupdf pymupdf4llm
python scripts/extract_pymupdf.py document.pdf              # Plain text
python scripts/extract_pymupdf.py document.pdf --markdown    # Markdown
python scripts/extract_pymupdf.py document.pdf --tables      # Tables
python scripts/extract_pymupdf.py document.pdf --images out/ # Extract images
python scripts/extract_pymupdf.py document.pdf --metadata    # Title, author, pages
python scripts/extract_pymupdf.py document.pdf --pages 0-4   # Specific pages
```

### marker-pdf (high-quality OCR)

```bash
# Check disk space first
python scripts/extract_marker.py --check

pip install marker-pdf
python scripts/extract_marker.py document.pdf                # Markdown
python scripts/extract_marker.py document.pdf --json         # JSON with metadata
python scripts/extract_marker.py scanned.pdf                 # Scanned PDF (OCR)
```

### Split, Merge & Search (pymupdf)

```python
# Split pages 1-5 to a new PDF
import pymupdf; doc = pymupdf.open("report.pdf"); new = pymupdf.open()
for i in range(5): new.insert_pdf(doc, from_page=i, to_page=i)
new.save("pages_1-5.pdf")

# Merge multiple PDFs
result = pymupdf.open()
for path in ["a.pdf", "b.pdf"]: result.insert_pdf(pymupdf.open(path))
result.save("merged.pdf")

# Search for text
doc = pymupdf.open("report.pdf")
for i, page in enumerate(doc):
    if page.search_for("revenue"):
        print(f"Page {i+1}: found")
```

See `scripts/extract_pymupdf.py` and `scripts/extract_marker.py` for helper scripts.

## Common Pitfalls

1. **weasyPrint for Chinese** — always use pandoc+xelatex for CJK
2. **web_extract first** — always try URL extraction before local
3. **marker-pdf disk space** — needs ~5GB; check with `--check` flag
4. **Page numbers in nano-pdf** — may be 0-based or 1-based; retry with ±1 if wrong
5. **No intermediate cleanup needed** — pandoc handles the full pipeline