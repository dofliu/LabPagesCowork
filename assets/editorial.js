/* DOF Lab — Editorial shared scripts */
(function () {
  'use strict';

  /* ---- mobile nav ---- */
  const toggle = document.querySelector('.nav__toggle');
  const links = document.querySelector('.nav__links');
  if (toggle && links) {
    toggle.addEventListener('click', () => links.classList.toggle('open'));
    links.querySelectorAll('a').forEach(a => a.addEventListener('click', () => links.classList.remove('open')));
  }

  /* ---- reveal on scroll ---- */
  const reveals = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window && reveals.length) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          const el = e.target;
          const d = el.getAttribute('data-reveal-delay');
          if (d) el.style.transitionDelay = d + 'ms';
          el.classList.add('in');
          io.unobserve(el);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    reveals.forEach(el => io.observe(el));
  } else {
    reveals.forEach(el => el.classList.add('in'));
  }

  /* ---- animate bars + counters when visible ---- */
  function animateValueEls(root) {
    (root || document).querySelectorAll('[data-bar]').forEach(el => {
      el.style.width = el.getAttribute('data-bar') + '%';
    });
    (root || document).querySelectorAll('[data-count]').forEach(el => {
      const target = parseFloat(el.getAttribute('data-count'));
      const dec = (el.getAttribute('data-count').indexOf('.') > -1) ? 1 : 0;
      const dur = 1300; const t0 = performance.now();
      function step(now) {
        const p = Math.min((now - t0) / dur, 1);
        const eased = 1 - Math.pow(1 - p, 3);
        el.textContent = (target * eased).toFixed(dec);
        if (p < 1) requestAnimationFrame(step);
        else el.textContent = target.toFixed(dec);
      }
      requestAnimationFrame(step);
    });
  }
  const statBlocks = document.querySelectorAll('[data-animate-block]');
  if ('IntersectionObserver' in window && statBlocks.length) {
    const io2 = new IntersectionObserver((entries) => {
      entries.forEach(e => { if (e.isIntersecting) { animateValueEls(e.target); io2.unobserve(e.target); } });
    }, { threshold: 0.3 });
    statBlocks.forEach(b => io2.observe(b));
  } else {
    animateValueEls(document);
  }

  /* ---- marquee: duplicate track for seamless loop ---- */
  document.querySelectorAll('.marquee__track').forEach(tr => {
    tr.innerHTML += tr.innerHTML;
  });

  /* ---- year in footer ---- */
  document.querySelectorAll('[data-year]').forEach(el => el.textContent = new Date().getFullYear());
})();

/* =========================================================================
   Projects renderer — used by projects.html (data.json driven)
   ========================================================================= */
window.DOFProjects = (function () {
  const CAT = {
    wind_energy:    { zh: '風力發電 AI',  cover: 'feat__cover--forest', ico: 'fa-wind' },
    industrial_ai:  { zh: '工業 AI 巡檢', cover: 'feat__cover--rust',   ico: 'fa-industry' },
    rag_knowledge:  { zh: 'RAG 知識',     cover: '',                    ico: 'fa-diagram-project' },
    edtech:         { zh: '教育科技',     cover: 'feat__cover--gold',   ico: 'fa-graduation-cap' },
    mcp_tools:      { zh: 'MCP 工具鏈',   cover: 'feat__cover--forest', ico: 'fa-plug' },
    personal_tools: { zh: '生產力工具',   cover: '',                    ico: 'fa-toolbox' },
    _other:         { zh: '其他',         cover: '',                    ico: 'fa-cube' },
  };
  const STATUS = {
    production: '營運中', active: '進行中', planning: '規劃中',
    planned: '規劃中', pending: '待啟動', completed: '已完成', development:'開發中', pilot:'教學試用', catalogued: '專案紀錄', research: '研究進行中', prototype: '研究原型', preprint: '預印本', published: '相關論文已發表'
  };

  function esc(s) { return String(s || '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }

  function card(p) {
    const c = CAT[p.category] || CAT._other;
    const tags = (p.technologies || []).slice(0, 3).map(t => `<span class="tag tag--ink">${esc(t)}</span>`).join('');
    const source = p.source_url || p.repository_url;
    const note = p.source_note || (p.last_updated ? `紀錄日期：${p.last_updated}` : '');
    return `
    <article class="feat feat--third" data-cat="${p.category || '_other'}" data-reveal>
      <div class="feat__cover ${c.cover}">
        <i class="fas ${c.ico} ico"></i>
        <span class="badge">${STATUS[p.status] || p.status || ''}</span>
      </div>
      <div class="feat__tags"><span class="tag">${c.zh}</span>${tags}</div>
      <h3>${esc(p.name_zh || p.name)}</h3>
      <p class="feat__desc">${esc(p.description_zh || p.description || '')}</p>
      <div class="feat__foot">
        <span class="feat__prog">${esc(note)}</span>
        ${source ? `<a href="${esc(source)}" class="read-more" target="_blank" rel="noopener">公開來源 ↗</a>` : ''}
      </div>
    </article>`;
  }

  function render(target, opts) {
    opts = opts || {};
    return fetch('data.json?v=20261010').then(r => r.json()).then(data => {
      let ps = (data.projects || []).slice();
      ps.sort((a, b) => Number(Boolean(b.source_url || b.repository_url)) - Number(Boolean(a.source_url || a.repository_url)));
      const el = document.querySelector(target);
      el.innerHTML = ps.map(card).join('');
      if (opts.onDone) opts.onDone(ps);
      // re-observe reveals
      el.querySelectorAll('[data-reveal]').forEach(x => x.classList.add('in'));
      return ps;
    }).catch(err => {
      const el = document.querySelector(target);
      if (el) el.innerHTML = '<p style="color:var(--muted)">專案資料載入失敗，請於 doflab.cc 線上瀏覽。</p>';
      console.error(err);
    });
  }
  return { render, CAT, STATUS };
})();


/* =========================================================================
   Showcase renderer — projects.html（showcase.json：封面＋短句，點開播動畫）
   ========================================================================= */
window.DOFShowcase = (function () {
  const CAT = {
    wind_energy: '風力發電 AI', industrial_ai: '工業 AI 巡檢', rag_knowledge: 'RAG 知識',
    edtech: '教育科技', mcp_tools: 'MCP 工具鏈', personal_tools: '生產力工具', other: '其他'
  };
  const SRC = { repo: 'GitHub Repo', document: '成果文件', link: '專案連結', other: '相關連結' };
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  let items = [];
  const fmt = s => { s = Math.round(s); return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0'); };

  function card(p) {
    return `<button type="button" class="sc-card" data-id="${esc(p.id)}" data-cat="${esc(p.category)}" aria-label="播放：${esc(p.title)}">
      <span class="sc-card__cover"><img src="${esc(p.cover)}" alt="" loading="lazy" width="960" height="540">
        <span class="sc-card__play" aria-hidden="true"><svg viewBox="0 0 16 16"><path d="M3 1.8v12.4c0 .6.7 1 1.2.6l9.6-6.2c.5-.3.5-1 0-1.3L4.2 1.2C3.7.9 3 1.2 3 1.8z"/></svg></span>
        ${p.duration ? `<span class="sc-card__dur">${fmt(p.duration)}</span>` : ''}</span>
      <span class="sc-card__body"><span class="tag">${esc(CAT[p.category] || CAT.other)}</span>
        <span class="sc-card__title">${esc(p.title)}</span>
        <span class="sc-card__tagline">${esc(p.tagline)}</span></span>
    </button>`;
  }

  function open(id) {
    const p = items.find(x => x.id === id); if (!p) return;
    const dlg = document.getElementById('sc-modal');
    const v = dlg.querySelector('video');
    v.poster = p.cover; v.src = p.video;
    dlg.querySelector('h2').textContent = p.title;
    dlg.querySelector('p').textContent = p.tagline;
    dlg.querySelector('.sc-modal__tech').innerHTML = (p.tech || []).map(t => `<span class="tag tag--ink">${esc(t)}</span>`).join('');
    const a = dlg.querySelector('.sc-modal__src');
    if (p.source_url) { a.href = p.source_url; a.innerHTML = `${SRC[p.source_type] || SRC.other} ↗`; a.hidden = false; } else { a.hidden = true; }
    if (typeof dlg.showModal === 'function') dlg.showModal(); else dlg.setAttribute('open', '');
    history.replaceState(null, '', '#' + p.id);
    const pr = v.play(); if (pr && pr.catch) pr.catch(() => {});
  }

  function close() {
    const dlg = document.getElementById('sc-modal');
    const v = dlg.querySelector('video'); v.pause(); v.removeAttribute('src'); v.load();
    if (dlg.open && dlg.close) dlg.close(); else dlg.removeAttribute('open');
    history.replaceState(null, '', location.pathname + location.search);
  }

  function render(gridSel, tabsSel) {
    const grid = document.querySelector(gridSel), tabs = document.querySelector(tabsSel);
    return fetch('showcase.json?v=20261031', { cache: 'no-cache' }).then(r => r.json()).then(data => {
      items = data.items || [];
      if (!items.length) { grid.innerHTML = '<p class="sc-empty">專案動畫製作中，敬請期待。</p>'; tabs.hidden = true; return items; }
      grid.innerHTML = items.map(card).join('');
      const cats = [...new Set(items.map(p => p.category))];
      if (cats.length < 2) tabs.hidden = true;
      else tabs.innerHTML = '<button class="tab active" data-filter="all">全部</button>' +
        cats.map(c => `<button class="tab" data-filter="${esc(c)}">${esc(CAT[c] || CAT.other)}</button>`).join('');
      tabs.addEventListener('click', e => {
        const b = e.target.closest('.tab'); if (!b) return;
        tabs.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t === b));
        const f = b.dataset.filter;
        grid.querySelectorAll('.sc-card').forEach(c => { c.style.display = (f === 'all' || c.dataset.cat === f) ? '' : 'none'; });
      });
      grid.addEventListener('click', e => { const c = e.target.closest('.sc-card'); if (c) open(c.dataset.id); });
      const dlg = document.getElementById('sc-modal');
      dlg.querySelector('.sc-modal__close').addEventListener('click', close);
      dlg.addEventListener('click', e => { if (e.target === dlg) close(); });
      dlg.addEventListener('cancel', e => { e.preventDefault(); close(); });
      if (location.hash.length > 1) open(decodeURIComponent(location.hash.slice(1)));
      return items;
    }).catch(err => {
      grid.innerHTML = '<p class="sc-empty">專案資料載入失敗，請稍後再試。</p>'; console.error(err);
    });
  }
  return { render, open, close };
})();

/* =========================================================================
   Announcements renderer — 首頁（前 N 則）與 news.html（全部）
   ========================================================================= */
window.DOFNews = (function () {
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  function row(n) {
    const t = n.link ? `<a href="${esc(n.link)}" target="_blank" rel="noopener">${esc(n.title)} ↗</a>` : esc(n.title);
    return `<article class="news-row${n.pinned ? ' news-row--pinned' : ''}">
      <time class="news-row__date" datetime="${esc(n.date)}">${esc(n.date.replace(/-/g, '.'))}</time>
      <div><div class="news-row__title">${t}</div>${n.body ? `<p class="news-row__body">${esc(n.body)}</p>` : ''}</div>
      <span class="tag">${esc(n.tag || '公告')}</span></article>`;
  }
  function render(target, opts) {
    opts = opts || {};
    const el = document.querySelector(target); if (!el) return Promise.resolve([]);
    return fetch('announcements.json?v=20261025', { cache: 'no-cache' }).then(r => r.json()).then(data => {
      let list = (data.items || []).slice().sort((a, b) => (b.pinned ? 1 : 0) - (a.pinned ? 1 : 0) || b.date.localeCompare(a.date));
      if (opts.limit) list = list.slice(0, opts.limit);
      if (!list.length) { if (opts.hideEmpty) opts.hideEmpty.hidden = true; else el.innerHTML = '<p style="color:var(--muted)">目前沒有公告。</p>'; return list; }
      el.innerHTML = list.map(row).join('');
      return list;
    }).catch(err => { if (opts.hideEmpty) opts.hideEmpty.hidden = true; console.error(err); });
  }
  return { render };
})();
