---
name: chinese-invoice-verification
description: >-
  发票验真 — Verify the authenticity of Chinese VAT invoices (增值税发票) on the
  official State Taxation Administration website (inv-veri.chinatax.gov.cn).
  Covers OCR extraction from invoice images, form filling, CAPTCHA handling,
  and result interpretation. Supports both traditional VAT invoices (12+8 digit)
  and fully-digital 全电发票/数电票 (20-digit).
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---

# 发票验真 — Chinese Invoice Verification
## Reference Files

- `references/captcha-ocr-techniques.md` — detailed CAPTCHA OCR pipeline (blue-channel extraction, HSV isolation, adaptive threshold, connected-component analysis, PSM mode selection).

## Trigger

Load this skill when the user asks to:
- Verify authenticity of a Chinese invoice (发票验真、发票查验、发票真伪)
- Check if a Chinese VAT invoice is genuine
- Look up an invoice on the national tax portal
- Any task involving the website `inv-veri.chinatax.gov.cn`

## Workflow

### Step 1: Get Invoice Image & Extract Data

When the user provides an invoice image (photo/screenshot), use OCR to extract these key fields:

| Field | Chinese Label | Format |
|-------|--------------|--------|
| Invoice Code | 发票代码 | 12 digits (traditional) |
| Invoice Number | 发票号码 | 8 digits (traditional) or 20 digits (全电发票) |
| Issue Date | 开票日期 | YYYYMMDD |
| Amount (excl. tax) | 开具金额(不含税) | Decimal, e.g. 1278.01 |
| Total Amount (incl. tax) | 价税合计 | Decimal, e.g. 1444.15 |
| Seller | 销售方名称 | Company name |
| Buyer | 购买方名称 | Company name |
| Tax ID | 纳税人识别号 | Unified social credit code |

**OCR approach for Chinese invoice images:**

```bash
# Install requirements
apt-get install -y tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-chi-tra
pip install pytesseract Pillow

# Basic OCR on invoice image
python3 -c "
import pytesseract
from PIL import Image
img = Image.open('invoice.jpg')
text = pytesseract.image_to_string(img, lang='chi_sim+chi_tra', config='--psm 6')
print(text)
"
```

**For better results:**
- Enlarge the image 2x before OCR: `img.resize((w*2, h*2), Image.LANCZOS)`
- Convert to grayscale before OCR: `img.convert('L')`
- Use `--psm 6` config for document-style layout
- Crop the image into sections (top = invoice code/number, middle = buyer/seller/items, bottom = totals)

### Step 2: Navigate to Verification Portal

URL: `https://inv-veri.chinatax.gov.cn/`

```python
browser_navigate(url="https://inv-veri.chinatax.gov.cn/")
```

**Known issues:**
- The page may show a warning: "您使用的是谷歌 XX版本浏览器，请参照操作说明安装根证书再进行发票查验操作！" — this can usually be dismissed/ignored; the form still works
- The browser environment uses a remote headless browser which may trigger browser version warnings
- If the page goes blank (empty snapshot), re-navigate to the URL

### Step 3: Fill in the Form

The website has these form fields (ref IDs may vary between sessions):

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| 发票代码 | textbox | No* | *For traditional invoices; leave empty for 全电发票 |
| 发票号码 | textbox | Yes | Enter full number |
| 开票日期 | textbox (YYYYMMDD) | Yes | Format: 20260206 |
| 开具金额(不含税) or 价税合计 | textbox | Yes | Depends on invoice type detection |
| 验证码 | textbox | Yes | CAPTCHA from image |

**Key distinction — invoice type detection:**
- **Traditional VAT invoice** (增值税发票): 发票代码 is 12 digits, 发票号码 is 8 digits. The amount field stays as "开具金额(不含税)".
- **全电发票/数电票** (fully-digital electronic invoice): The invoice number is a single 20-digit string (e.g. `26117000000218619587`). When you enter the full 20-digit number, the website auto-detects the type and **changes the amount field label** from "开具金额(不含税)" to "价税合计" (total including tax).

**Procedure:**
```python
# Enter the invoice number FIRST to trigger type detection
browser_type(ref="@e15", text="invoice_number_here")

# Check snapshot to see if field label changed
browser_snapshot()

# Then enter date, amount, and CAPTCHA
browser_type(ref="@e23", text="YYYYMMDD")
browser_type(ref="@e16", text="amount")
```

### Step 4: Handle CAPTCHA

The CAPTCHA is a **120×50 PNG image with blue text** on a noisy gray background, generated client-side via JavaScript. **Self-service OCR is unreliable** (~40-60% accuracy), but possible with the right techniques.

**CAPTCHA Extraction:**

After clicking the refresh link, extract the base64 CAPTCHA data:

```python
browser_click(ref="CAPTCHA_REF")  # "点击图片刷新" link

# Extract base64 image data
result = browser_console(
    expression="Array.from(document.querySelectorAll('img')).filter(i => i.src.length > 500).map(i => i.src)[0]"
)
```

**OCR Pipeline (see `references/captcha-ocr-techniques.md` for full code):**

```
1. Decode base64 → PIL Image
2. Isolate blue text (B - max(R,G) difference)
3. Threshold (value >= 15)
4. Dilate to connect broken strokes (2×2 kernel, 1 iteration)
5. Resize 4× (480×200) for tesseract
6. OCR with --psm 8, whitelist: 0-9 A-Z a-z
```

Fallback order:
1. Try OCR with blue-diff method + PSM 8
2. Verify plausibility (4 chars, seems reasonable)
3. Submit; if CAPTCHA error → refresh CAPTCHA → retry OCR
4. After 3 failed attempts → **ask the user** to read the CAPTCHA

```python
# Click the CAPTCHA image to refresh it
browser_click(ref="CAPTCHA_REF")  # e.g. e21 or e24 — varies per session
```

### Step 5: Submit Verification

Once all fields (including CAPTCHA) are filled, the "查 验" button should become enabled. Click it:

```python
browser_click(ref="@e18")  # Click 查验 button
```

Then read the result from the page snapshot.

### Step 6: Interpret Results

Expected results from the website:
- **发票信息一致 (一致)** ⭐ — genuine invoice, data matches
- **不一致** — data mismatch (double-check your input)
- **查无此票** — no such invoice in the system (possible fraud or data entry error)
- **已超过查验次数** — this invoice has been checked more than 5 times today (daily limit)

## Pitfalls

1. **CAPTCHA is unreliable for OCR** — always prefer asking the user after 3 failed OCR attempts. Tax verification CAPTCHAs use colored, distorted text specifically designed to defeat automated reading. See `references/captcha-ocr-techniques.md` for the best-known OCR pipeline.

2. **Browser session may go empty frequently** — browser_snapshot returning "(empty page)" happens very often (after every click navigation in some sessions). Re-navigate immediately: `browser_navigate(url="https://inv-veri.chinatax.gov.cn/")`. Expect to re-navigate 3-5+ times during a single verification session.

3. **Ref IDs are unstable across navigations** — the form field ref IDs (e.g. e15 vs e17, e20 vs e23) change every time you re-navigate. Always call browser_navigate → inspect snapshot for current refs before typing into fields. Never hardcode ref IDs across navigations.

4. **Invoice type auto-detection** — the website detects 全电发票 from the 20-digit number and changes the amount field. Always enter the invoice number FIRST before date and amount.

5. **Daily limit** — each invoice can be checked max 5 times per day.

5. **Invoice image from mobile app** — images may include phone UI chrome (battery, time, navigation bars, AI buttons). Skip these overlays when cropping for OCR.

6. **Amount field name changes** — for 全电发票, the field changes from "开具金额(不含税)" to "价税合计". Enter 1278.01 for the former and 1444.15 for the latter in the example invoice above.

7. **Invoice code field** — for 全电发票, leave the 发票代码 field empty. The error "发票代码有误!" appears when you try to enter a code for a 全电发票.

## Example Session Flow

```
用户: 帮我查验这张发票

1. Get invoice image → OCR extract:
   - 发票号码: 26117000000218619587
   - 开票日期: 20260206
   - 金额: 1278.01 (不含税) / 1444.15 (价税合计)
   - 销售方: 小米通讯技术有限公司
   - 购买方: 一汽丰田汽车有限公司天津(总部)工厂工会委员会

2. Navigate to https://inv-veri.chinatax.gov.cn/
3. Enter: 发票号码=26117000000218619587, 日期=20260206
4. Check if field label changed → if "价税合计" enter 1444.15, else enter 1278.01
5. Ask user for CAPTCHA text
6. Enter CAPTCHA, click 查 验
7. Report result to user
```