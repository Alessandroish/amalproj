// Fit each [data-fit] word to its box: width by font-size, height by vertical stretch (condensed poster look).
document.fonts.ready.then(() => {
  document.querySelectorAll('[data-fit]').forEach(el => {
    const W = el.parentElement.clientWidth, H = +el.dataset.h * 3.7795, off = +(el.dataset.top || 0) * 3.7795;
    el.style.fontSize = '100px';
    const r = el.getBoundingClientRect();
    const fs = 100 * W / r.width; el.style.fontSize = fs + 'px';
    const cap = fs * 0.83;               // Oswald cap height ≈ .83em incl. ascent offset
    const sy = H ? H / cap : 1;
    el.style.transform = `translateY(${off - fs*0.13*sy}px) scaleY(${sy})`;
  });
  document.body.dataset.ready = '1';
});
