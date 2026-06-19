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
    planned: '規劃中', pending: '待啟動', completed: '已完成'
  };

  function esc(s) { return (s || '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])); }

  function card(p) {
    const c = CAT[p.category] || CAT._other;
    const tags = (p.technologies || []).slice(0, 3).map(t => `<span class="tag tag--ink">${esc(t)}</span>`).join('');
    const prog = p.progress || 0;
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
        <span class="feat__prog"><b>${prog}%</b> ${p.key_metrics ? '· ' + esc(p.key_metrics) : ''}</span>
      </div>
    </article>`;
  }

  function render(target, opts) {
    opts = opts || {};
    return fetch('data.json').then(r => r.json()).then(data => {
      let ps = (data.projects || []).slice();
      ps.sort((a, b) => (b.progress || 0) - (a.progress || 0));
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
