/* DOF Lab — bilingual runtime (繁體中文 / English)
 *
 * 用法：每頁 <head> 放 <script src="assets/i18n.js?v=..."></script>（在 editorial.js 之前）。
 * 原始頁面一律是繁體中文；英文翻譯放在 assets/i18n/en.js（window.DOF_I18N_EN），
 * 以「元素的中文 innerHTML（空白正規化後）」當 key，對不到的字串維持中文（不會壞頁）。
 *
 * 語言決定順序：?lang=en|zh（並記住）→ localStorage → 瀏覽器語言（非中文 → 英文）。
 * 切換語言 = 寫入 localStorage 後重新載入（最單純、最不會漏）。
 *
 * 工具：node tools/i18n/extract_keys.js 列出各頁待翻譯字串；python3 tools/i18n/check_missing.py 找缺漏。
 */
(function () {
  'use strict';
  var KEY = 'doflab-lang', VER = '20261106';
  var lang = null;
  try {
    var q = new URLSearchParams(location.search).get('lang');
    if (q === 'en' || q === 'zh') { lang = q; try { localStorage.setItem(KEY, lang); } catch (e) {} }
    if (!lang) { try { lang = localStorage.getItem(KEY); } catch (e) {} }
  } catch (e) {}
  if (lang !== 'en' && lang !== 'zh') {
    var nl = String(navigator.language || navigator.userLanguage || 'zh').toLowerCase();
    lang = nl.indexOf('zh') === 0 ? 'zh' : 'en';
  }
  var EN = lang === 'en';
  var root = document.documentElement;
  root.lang = EN ? 'en' : 'zh-Hant';
  root.setAttribute('data-lang', lang);

  // 英文：同步載入字典並先隱藏 body，套用完再顯示（避免中文閃一下）
  if (EN) {
    var base = (document.currentScript && document.currentScript.src) ? document.currentScript.src.replace(/assets\/i18n\.js.*$/, '') : '';
    document.write('<style id="i18n-hide">body{visibility:hidden}</style>' +
      '<script src="' + base + 'assets/i18n/en.js?v=' + VER + '"><\/script>');
  }

  var CJK = /[⺀-鿿豈-﫿＀-￯]/;
  var INLINE = { A: 1, SPAN: 1, STRONG: 1, B: 1, EM: 1, I: 1, SMALL: 1, CODE: 1, BR: 1, SUP: 1, SUB: 1, TIME: 1, U: 1, MARK: 1, KBD: 1, ABBR: 1 };
  var SKIP = { SCRIPT: 1, STYLE: 1, NOSCRIPT: 1, TEMPLATE: 1, SVG: 1, VIDEO: 1, CANVAS: 1, IFRAME: 1 };
  var ATTRS = ['aria-label', 'placeholder', 'alt', 'title'];

  function norm(s) { return String(s == null ? '' : s).replace(/\s+/g, ' ').trim(); }
  function hasCJK(s) { return CJK.test(s); }
  function ownText(el) {
    var t = '';
    for (var n = el.firstChild; n; n = n.nextSibling) if (n.nodeType === 3) t += n.nodeValue;
    return t;
  }
  function hasBlockChild(el) {
    for (var i = 0; i < el.children.length; i++) { var c = el.children[i]; if (!INLINE[c.tagName] || hasBlockChild(c)) return true; }
    return false;
  }

  /** 走訪 DOM，對每個「可翻譯葉節點」呼叫 fn(el, key)。規則見檔頭。 */
  function walk(el, fn) {
    if (!el || el.nodeType !== 1 || SKIP[el.tagName] || el.hasAttribute('data-i18n-skip')) return;
    if (!hasCJK(el.textContent)) return;
    var kids = [], i;
    for (i = 0; i < el.children.length; i++) if (hasCJK(el.children[i].textContent)) kids.push(el.children[i]);
    var own = hasCJK(ownText(el));
    if (!own && kids.length === 1) return walk(kids[0], fn);
    var inlineOnly = true;
    for (i = 0; i < kids.length; i++) if (!INLINE[kids[i].tagName] || hasBlockChild(kids[i]) || kids[i].hasAttribute('data-i18n-skip')) { inlineOnly = false; break; }
    if (inlineOnly && (own || kids.length)) { fn(el, norm(el.innerHTML)); return; }
    for (i = 0; i < kids.length; i++) walk(kids[i], fn);
  }

  function dict() { return window.DOF_I18N_EN || null; }
  function lookup(key) {
    var d = dict(); if (!d) return null;
    if (d.strings && Object.prototype.hasOwnProperty.call(d.strings, key)) return d.strings[key];
    var rules = d.rules || [];
    for (var i = 0; i < rules.length; i++) {
      var re = rules[i]._re || (rules[i]._re = new RegExp(rules[i][0]));
      if (re.test(key)) return key.replace(re, rules[i][1]);
    }
    return null;
  }

  function translateAttrs(el) {
    var els = [el].concat(Array.prototype.slice.call(el.querySelectorAll('[aria-label],[placeholder],[alt],[title]')));
    els.forEach(function (e) {
      if (e.nodeType !== 1) return;
      ATTRS.forEach(function (a) {
        var v = e.getAttribute && e.getAttribute(a);
        if (v && hasCJK(v)) { var t = lookup(norm(v)); if (t != null) e.setAttribute(a, t); }
      });
    });
  }

  /** 把 root 底下的中文葉節點換成英文（找不到翻譯的保持中文）。 */
  function apply(rootEl) {
    if (!EN || !dict()) return 0;
    var n = 0;
    walk(rootEl || document.body, function (el, key) {
      if (el.hasAttribute('data-i18n')) return;
      var t = lookup(key);
      if (t != null) { el.innerHTML = t; el.setAttribute('data-i18n', '1'); n++; }
    });
    translateAttrs(rootEl || document.body);
    return n;
  }

  function applyHead() {
    var t = lookup(norm(document.title)); if (t != null) document.title = t;
    ['description', 'og:title', 'og:description'].forEach(function (name) {
      var m = document.querySelector('meta[name="' + name + '"],meta[property="' + name + '"]');
      if (m) { var v = m.getAttribute('content'); if (v && hasCJK(v)) { var tt = lookup(norm(v)); if (tt != null) m.setAttribute('content', tt); } }
    });
  }

  function reveal() { var s = document.getElementById('i18n-hide'); if (s) s.parentNode.removeChild(s); }

  function switchTo(next) {
    var saved = false;
    try { localStorage.setItem(KEY, next); saved = localStorage.getItem(KEY) === next; } catch (e) {}
    var u = new URL(location.href);
    // localStorage 不可用（隱私模式／被封鎖）時改用網址參數記住語言
    if (saved) u.searchParams.delete('lang'); else u.searchParams.set('lang', next);
    if (u.toString() === location.href) location.reload(); else location.href = u.toString();
  }

  /** 導覽列語言切換鈕（自動注入 .nav__links 的 CTA 前） */
  function injectToggle() {
    var links = document.querySelector('.nav__links');
    if (!links || links.querySelector('.nav__lang')) return;
    var li = document.createElement('li'); li.className = 'nav__lang'; li.setAttribute('data-i18n-skip', '');
    var b = document.createElement('button'); b.type = 'button'; b.className = 'lang-toggle';
    b.setAttribute('aria-label', EN ? '切換為中文' : 'Switch to English');
    b.innerHTML = '<span class="' + (EN ? '' : 'on') + '">中</span><span class="sep">/</span><span class="' + (EN ? 'on' : '') + '">EN</span>';
    b.addEventListener('click', function () { switchTo(EN ? 'zh' : 'en'); });
    li.appendChild(b);
    var cta = links.querySelector('.nav__cta');
    if (cta && cta.parentNode && cta.parentNode.parentNode === links) links.insertBefore(li, cta.parentNode); else links.appendChild(li);
  }

  function observe() {
    if (!EN || !('MutationObserver' in window)) return;
    var mo = new MutationObserver(function (recs) {
      recs.forEach(function (r) {
        for (var i = 0; i < r.addedNodes.length; i++) {
          var n = r.addedNodes[i];
          if (n.nodeType === 1) { if (!n.closest || !n.closest('[data-i18n]')) apply(n); }
          else if (n.nodeType === 3 && n.parentElement && hasCJK(n.nodeValue) && !n.parentElement.closest('[data-i18n]')) apply(n.parentElement);
        }
      });
    });
    mo.observe(document.body, { childList: true, subtree: true });
  }

  /** 給頁面腳本用：DOFI18n.t('中文', 'English') */
  function t(zh, en) { return EN ? en : zh; }
  /** 給資料驅動內容用：挑物件的 *_en 欄位 */
  function f(obj, field) { if (!obj) return ''; return (EN && obj[field + '_en']) ? obj[field + '_en'] : (obj[field] || ''); }

  window.DOFI18n = { lang: lang, en: EN, t: t, f: f, apply: apply, walk: walk, norm: norm, switchTo: switchTo, lookup: lookup, hasCJK: hasCJK };

  function init() {
    if (EN) { applyHead(); apply(document.body); observe(); }
    injectToggle();
    reveal();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  setTimeout(reveal, 2500); // 字典沒載到也要顯示頁面
})();
