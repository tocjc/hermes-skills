# PDF Generation Practice Examples

## Standard Workflow

```bash
# 1. Render
pandoc report.md \
  --pdf-engine=xelatex \
  -V mainfont="Noto Sans CJK SC" \
  -V CJKmainfont="Noto Sans CJK SC" \
  -V geometry:margin=2.5cm \
  -o report.pdf

# 2. Verify font embedding
python3 -c "print(open('report.pdf','rb').read().count(b'CIDFontType0C'))"
# Expected: ≥2
```

## Cross-Platform Readability Verification

```bash
python3 -c "
data = open('report.pdf','rb').read()
cid = data.count(b'CIDFontType0C')
ref = data.count(b'/FontFile')
print(f'Embedded CIDFonts: {cid}')
print(f'External refs: {ref}')
# CID ≥ 2, ref ≈ 0 → fully embedded
"
```

## If Report Contains Mermaid Diagrams

xelatex does not support Mermaid. Solutions:
1. Install `mmdc` (mermaid-cli) to convert to PNG
2. Replace mermaid blocks with `<img src="diagram.png">` before pandoc
3. Better: use ASCII art diagrams instead (boxes, pixel-art skills)

## Long Code Line Wrapping

xelatex doesn't auto-wrap code blocks by default:
```bash
cat report.md | fold -s -w 80 > report_wrapped.md
pandoc report_wrapped.md --pdf-engine=xelatex ... -o report.pdf
```

## Chinese-English Mixed Font Settings

```bash
pandoc report.md \
  --pdf-engine=xelatex \
  -V mainfont="Noto Sans" \
  -V CJKmainfont="Noto Sans CJK SC" \
  -V monofont="Fira Code" \
  -o report.pdf
```