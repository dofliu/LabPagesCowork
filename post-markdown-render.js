(function () {
  const article = document.querySelector('.article-content');
  if (!article) return;

  const raw = article.textContent ? article.textContent.trim() : '';
  if (!raw) return;

  const markdownSignal = /(^|\n)#{1,6}\s|\*\*[^*]+\*\*|(^|\n)-\s|```|(^|\n)>\s/m;
  if (!markdownSignal.test(raw)) return;

  if (window.marked && typeof window.marked.parse === 'function') {
    article.innerHTML = window.marked.parse(raw, { gfm: true, breaks: true });
    return;
  }

  article.textContent = raw.replace(/\*\*(.*?)\*\*/g, '$1');
})();
