#!/usr/bin/env node
/* 列出每個頁面「需要英文翻譯」的中文字串（與 assets/i18n.js 的走訪規則完全一致，因為直接在真實 DOM 裡跑同一支程式）。
 *
 *   node tools/i18n/extract_keys.js                 # 所有根目錄頁面 → tools/i18n/keys.json
 *   node tools/i18n/extract_keys.js index.html      # 只看某幾頁
 *
 * 輸出格式：{ "<page>": { "strings": [...], "attrs": [...], "head": [...] } }
 * 之後用 python3 tools/i18n/check_missing.py 對照 assets/i18n/en.js 找缺漏。
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..', '..');
const PAGES = process.argv.length > 2 ? process.argv.slice(2)
  : ['index.html', 'about.html', 'lab.html', 'research.html', 'projects.html', 'publications.html', 'blog.html',
     'news.html', 'contact.html', 'github.html', 'repos.html', 'privacy.html'];

(async () => {
  const exe = process.env.CHROMIUM_PATH;
  const browser = await chromium.launch(exe ? { executablePath: exe } : {});
  const out = {};
  for (const p of PAGES) {
    const page = await browser.newPage();
    // 不讓頁面自己的 fetch/JS 執行（只看靜態內容）；i18n.js 以 zh 模式載入，不改 DOM
    await page.route('**/*', r => (r.request().resourceType() === 'document' ? r.continue() : r.abort()));
    await page.addInitScript(() => { try { localStorage.setItem('doflab-lang', 'zh'); } catch (e) {} });
    await page.goto('file://' + path.join(ROOT, p), { waitUntil: 'domcontentloaded' });
    await page.addScriptTag({ path: path.join(ROOT, 'assets', 'i18n.js') });
    const res = await page.evaluate(() => {
      const I = window.DOFI18n, strings = [], attrs = [], head = [];
      I.walk(document.body, (el, key) => { if (!strings.includes(key)) strings.push(key); });
      document.querySelectorAll('[aria-label],[placeholder],[alt],[title]').forEach(e => {
        ['aria-label', 'placeholder', 'alt', 'title'].forEach(a => { const v = e.getAttribute(a); if (v && I.hasCJK(v) && !attrs.includes(I.norm(v))) attrs.push(I.norm(v)); });
      });
      head.push(I.norm(document.title));
      document.querySelectorAll('meta[name="description"],meta[property="og:title"],meta[property="og:description"]').forEach(m => {
        const v = m.getAttribute('content'); if (v && I.hasCJK(v)) head.push(I.norm(v));
      });
      return { strings, attrs, head };
    });
    out[p] = res;
    console.error(`${p}: ${res.strings.length} strings, ${res.attrs.length} attrs, ${res.head.length} head`);
    await page.close();
  }
  await browser.close();
  const dest = path.join(__dirname, 'keys.json');
  fs.writeFileSync(dest, JSON.stringify(out, null, 2) + '\n');
  console.error('→ ' + path.relative(ROOT, dest));
})();
