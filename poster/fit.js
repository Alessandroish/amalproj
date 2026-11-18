// Scale title so the first (widest) row fills the poster width; other rows share the size.
document.fonts.ready.then(() => {
  const t = document.querySelector('.title'); const rows = t.querySelectorAll('.row');
  rows.forEach(r => r.style.fontSize = '100px');
  const w = t.clientWidth, first = rows[0];
  const span = document.createElement('span'); span.innerHTML = first.innerHTML; span.style.whiteSpace='nowrap';
  first.innerHTML=''; first.appendChild(span);
  const size = 100 * w / span.getBoundingClientRect().width;
  rows.forEach(r => r.style.fontSize = size + 'px');
  document.body.dataset.ready = '1';
});
