/**
 * zhihu-browser-search.js
 *
 * 知乎搜索爬虫：用 puppeteer + 用户 Cookie 登录知乎搜索关键词。
 *
 * 用法：
 *   NODE_PATH=$(npm root -g) node zhihu-browser-search.js "关键词"
 *
 * 环境变量：
 *   ZHIHU_COOKIE   必填。从浏览器开发者工具 → Application → Cookies → zhihu.com
 *                  复制 `z_c0` 的值（整个 cookie 字符串也可以）。
 *
 * 输出：JSON 格式结果数组 [{title, url, summary, voteCount}]
 *
 * 注意事项：
 *   1. 需要先通过 apt 安装 chromium-browser（腾讯镜像最快）
 *   2. 只爬搜索列表页，不进入单个 answer 详情页（详情页有额外反爬 403）
 *   3. Cookie 约 7 天过期，过期后需用户重新提供
 *   4. puppeteer v22+ 已弃用 headless:'new'，改用 headless:true
 */

const puppeteer = require('puppeteer');
const { URL } = require('url');

const keyword = process.argv[2];
if (!keyword) {
  console.error('用法: node zhihu-browser-search.js "搜索关键词"');
  process.exit(1);
}

const ZHIHU_COOKIE = process.env.ZHIHU_COOKIE;
if (!ZHIHU_COOKIE) {
  console.error('请设置环境变量 ZHIHU_COOKIE（从浏览器复制知乎 Cookie）');
  process.exit(1);
}

(async () => {
  const browser = await puppeteer.launch({
    executablePath: '/usr/bin/chromium-browser',
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
    ],
  });

  try {
    const page = await browser.newPage();
    await page.setUserAgent(
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
      '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    );
    await page.setExtraHTTPHeaders({
      'Accept-Language': 'zh-CN,zh;q=0.9',
    });

    // 设置 Cookie（登录态）
    const cookieParts = ZHIHU_COOKIE.split(';').reduce((acc, part) => {
      const [k, ...v] = part.trim().split('=');
      if (k) acc[k.trim()] = v.join('=');
      return acc;
    }, {});
    const cookies = Object.entries(cookieParts).map(([name, value]) => ({
      name,
      value,
      domain: '.zhihu.com',
      path: '/',
      httpOnly: false,
      secure: true,
    }));
    await page.setCookie(...cookies);

    // 搜索
    const searchUrl = `https://www.zhihu.com/search?type=content&q=${encodeURIComponent(keyword)}`;
    await page.goto(searchUrl, { waitUntil: 'networkidle2', timeout: 30000 });

    // 等搜索结果渲染
    await page.waitForSelector('.SearchResult-items, [data-za-module="SearchResultItem"]', {
      timeout: 15000,
    }).catch(() => {});

    // 提取结果
    const results = await page.evaluate(() => {
      const items = document.querySelectorAll(
        '.SearchResult-items [data-za-module="SearchResultItem"], ' +
        '.SearchResult-items .List-item'
      );
      return Array.from(items).slice(0, 15).map(item => {
        const titleEl = item.querySelector('h2 a, .ContentItem-title a');
        const summaryEl = item.querySelector('.RichText, .SearchItem-description');
        const voteEl = item.querySelector('.Voters .NumberBoard-item .NumberBoard-num, .ZmItem_Voted');
        return {
          title: titleEl?.textContent?.trim() || '',
          url: titleEl?.getAttribute('href') || '',
          summary: summaryEl?.textContent?.trim().slice(0, 200) || '',
          voteCount: voteEl?.textContent?.trim() || '',
        };
      }).filter(r => r.title);
    });

    // 输出 JSON
    console.log(JSON.stringify({
      keyword,
      resultCount: results.length,
      results,
      timestamp: new Date().toISOString(),
    }, null, 2));

  } catch (err) {
    console.error(JSON.stringify({ error: err.message }));
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
