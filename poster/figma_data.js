// Dump everything needed to rebuild an HTML poster natively in Figma:
// raster layers (PNG/JPEG files), ink boxes of the huge titles, text lines with styles, stars/icons.
// Usage: node figma_data.js poster-law-halftone <outdir>
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const name = process.argv[2] || 'poster-law-halftone';
const out = process.argv[3] || 'figma-data';
const W = 1123, H = 1587, S = 2;
fs.mkdirSync(out, { recursive: true });

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: S });
  await page.goto('file://' + path.resolve(name + '.html'), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => document.querySelectorAll('q').forEach(q => { q.style.quotes = 'none'; q.textContent = '«' + q.textContent + '»'; }));

  const layers = await page.evaluate(() => [...document.querySelector('.poster').children].map((el, i) => {
    el.dataset.fx = i; return { i, tag: el.tagName.toLowerCase(), cls: el.getAttribute('class') || '', id: el.id || '' };
  }));

  const texts = await page.evaluate(() => {
    const res = [];
    document.querySelectorAll('.top, .right, .left, .cite, .reg, .credit').forEach(block => {
      const walker = document.createTreeWalker(block, NodeFilter.SHOW_TEXT); const items = [];
      while (walker.nextNode()) {
        const node = walker.currentNode; const txt = node.textContent; if (!txt.trim()) continue;
        const cs = getComputedStyle(node.parentElement); const re = /\S+\s*/g; let m;
        while ((m = re.exec(txt))) {
          const r = document.createRange(); r.setStart(node, m.index); r.setEnd(node, m.index + m[0].trimEnd().length);
          const rect = r.getBoundingClientRect(); if (rect.width) items.push({ word: m[0], rect, cs });
        }
      }
      const lines = [];
      items.forEach(it => {
        const key = `${Math.round(it.rect.top)}|${it.cs.fontSize}|${it.cs.fontWeight}|${it.cs.color}|${it.cs.fontStyle}`;
        let ln = lines.find(l => l.key === key);
        if (!ln) { ln = { key, words: [], l: 1e9, r: -1e9, t: it.rect.top, b: it.rect.bottom, cs: it.cs }; lines.push(ln); }
        ln.words.push(it.word); ln.l = Math.min(ln.l, it.rect.left); ln.r = Math.max(ln.r, it.rect.right);
      });
      lines.forEach(ln => {
        const cs = ln.cs; let text = ln.words.join('').trimEnd();
        if (cs.textTransform === 'uppercase') text = text.toUpperCase();
        res.push({ block: block.className, text, left: ln.l, right: ln.r, top: ln.t, bottom: ln.b,
          family: cs.fontFamily.split(',')[0].replace(/["']/g, '').trim(), size: parseFloat(cs.fontSize),
          weight: +cs.fontWeight, italic: cs.fontStyle === 'italic', color: cs.color,
          ls: cs.letterSpacing === 'normal' ? 0 : parseFloat(cs.letterSpacing), align: getComputedStyle(block).textAlign });
      });
    });
    return res;
  });

  const vectors = await page.evaluate(() => [...document.querySelectorAll('.poster > svg.star, .reg svg')].map(s => {
    const r = s.getBoundingClientRect();
    return { x: r.left, y: r.top, w: r.width, h: r.height, vb: s.getAttribute('viewBox'), inner: s.innerHTML, id: s.id || '', icon: !!s.closest('.reg') };
  }));

  async function only(i) {
    await page.evaluate(i => {
      document.querySelectorAll('[data-fx]').forEach(el => el.style.display = el.dataset.fx == i ? '' : 'none');
      document.documentElement.style.background = document.body.style.background = document.querySelector('.poster').style.background = 'transparent';
    }, i);
  }
  const rasters = [];
  const titles = [];
  for (const L of layers) {
    let label = null, opaque = false;
    if (L.cls === 'layer' && L.i === 0) { label = 'paper'; opaque = true; }
    else if (L.id === 'torn') label = 'torn';
    else if (L.cls === 'statue') label = 'statue';
    else if (L.tag === 'svg' && L.cls === 'layer') label = L.i < 8 ? 'shade' : 'wear';
    if (label) {
      await only(L.i);
      const file = path.join(out, label + (opaque ? '.jpg' : '.png'));
      await page.screenshot({ path: file, omitBackground: !opaque, type: opaque ? 'jpeg' : 'png', quality: opaque ? 90 : undefined });
      rasters.push({ label, file, order: L.i, bytes: fs.statSync(file).size });
    }
    if (['t1', 't2a', 't2b'].includes(L.id)) {
      await only(L.i);
      const file = path.join(out, L.id + '.png');
      await page.screenshot({ path: file, omitBackground: true });
      const info = await page.evaluate(id => { const el = document.getElementById(id);
        return { html: el.innerHTML, color: getComputedStyle(el).color, red: el.querySelector('.r') ? getComputedStyle(el.querySelector('.r')).color : null }; }, L.id);
      titles.push({ id: L.id, file, order: L.i, ...info });
    }
  }
  fs.writeFileSync(path.join(out, 'data.json'), JSON.stringify({ W, H, S, layers, rasters, titles, texts, vectors }, null, 1));
  console.log(JSON.stringify(rasters), titles.length, texts.length, vectors.length);
  await browser.close();
})();
