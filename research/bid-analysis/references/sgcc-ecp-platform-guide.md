# State Grid ECP Platform Access Guide

**国家电网新一代电子商务平台 (ECP v2.0)**
URL: https://ecp.sgcc.com.cn/ecp2.0/portal/#/

## Key Facts

- **Access method**: Browser only (SPA — Single Page Application, JavaScript required). curl/wget cannot render the content.
- **Login**: Not required for browsing public announcements. The "登录" button can be ignored.
- **Anti-bot**: Uses Cloudflare (like other Chinese platforms). The browser may show "Verifying you are human" — clicking the checkbox usually resolves.
- **Search**: Two search modes:
  1. **顶部全文检索** (top full-text search) — searches all announcement types
  2. **栏目内搜索** (section-specific search) — within each subsection

## Navigation Flow

### Homepage → 采购公告 (Procurement Announcements)
```
1. browser_navigate("https://ecp.sgcc.com.cn/ecp2.0/portal/#/")
2. browser_click("招标采购")  [left sidebar menu]
3. browser_click("采购公告")  [sub-menu]
4. Search fields appear:
   - 项目状态 dropdown (ref=e4): "请选择项目状态" / "正在采购" / "已经截止"
   - 招标单位 textbox (ref=e5): type the bidding entity
   - 项目编号 textbox (ref=e6): type project number
   - 关键字 textbox (ref=e7): type keywords
   - 查询 button (ref=e8): click to search
5. browser_type(ref=e7, text="国网冀北") then browser_click(ref=e8)
6. Results table loads with: 项目名称, 项目编号, 项目状态, 创建时间
7. browser_click on a row to see detailed announcement
```

### Homepage → 招标公告及投标邀请书 (Tender Announcements & Bid Invitations)
```
Same flow as above, but click "招标公告及投标邀请书" instead of "采购公告"
```

### Full-Text Search (from any page)
```
1. Locate the top search bar:
   - combobox (ref=e23/e25): "全文检索" (default, leave as-is)
   - textbox (ref=e24/e26): type keywords
   - search button (ref=e25/e27): magnifying glass icon
2. browser_type(ref=e26, text="国网冀北 群众性创新") then browser_click(ref=e27)
```

## Search Tips

| Goal | Strategy |
|------|----------|
| Find specific company's bids | Type company name in 招标单位 textbox |
| Find by project type | Use 关键字 with terms like 创新, 服务, 物资, 施工 |
| Filter by status | Set 项目状态 to "正在采购" for active, "已经截止" for past |
| Broad scan | Type just "冀北" in 关键字 — finds all Jibei-related entries |
| Skip result | Empty table = no matches for that keyword in that section |

## Critical Section Selection: 招标公告 vs 采购公告

⚠️ **For 国网冀北 monitoring, 招标公告及投标邀请书 is the productive section; 采购公告 is not.**

| Section | 国网冀北 Results | Why |
|---------|:----------------:|-----|
| **采购公告** | All expired (last active: 2026-05-25) | Procurement notices for already-closed competitive negotiations |
| **招标公告及投标邀请书** | **Active (正在招标)** | Open tender announcements — has 5+ active 国网冀北 projects in June 2026 |
| **资格预审公告** | 1 result (2023) | Only old pre-qualification projects |

**Search flow that works:**
1. Navigate to homepage, click 招标采购 in sidebar, then 招标公告及投标邀请书
2. Use the **section-specific search form** (NOT the top full-text search bar):
   - 关键字 textbox (ref=e7): type "国网冀北"
   - 查询 button (ref=e9): click to search
3. Read results table — columns: 项目名称, 项目编号, 项目状态, 创建时间

**Combobox workaround:** When clicking option elements in the homepage combobox fails with "Could not compute box model", use JavaScript via browser_console to select the option:

## Known Ref Patterns (from observed session)

On the 采购公告 page:
- @e4 = 项目状态 dropdown
- @e5 = 招标单位 textbox
- @e6 = 项目编号 textbox
- @e7 = 关键字 textbox
- @e8 = 查询 button
- @e9 = 清除 button

On the top search bar:
- @e23 = combobox (全文检索 selector)
- @e24 = textbox
- @e25 = search button

**Note**: Ref IDs may change between sessions. Always use browser_snapshot() to confirm current IDs.

## What NOT to Expect

- **Internal innovation projects** (群众性创新项目, QC小组, 五小活动) — these are run through internal OA / trade union, not on ECP
- **Project technical details** — bid notices on ECP are legal/administrative documents, not technical specs. For technical depth, use Google Patents instead
- **Bid amounts** — many ECP notices do NOT show amounts publicly. Amounts may require registration/login to view
- **Buyer contact info** — contact info may be redacted in public view
