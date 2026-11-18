// Dump a poster that marks its layers with data-name / data-raster (and .txt text blocks) for a native Figma build:
// every raster layer as its own PNG with its box (CSS px = Figma px in a 1123x1587 frame),
// every text block as lines with font, size, weight, colour, letter-spacing and position.
// Usage: node figma_layers.js poster-networking-blue <outdir>
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const name = process.argv[2], out = process.argv[3] || 'figma-layers';
const W = 1123, H = 1587, S = 2;
fs.mkdirSync(out, { recursive: true });
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: S });
  await page.goto('file://' + path.resolve(name + '.html'), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready); await page.waitForTimeout(400);
  const layers = await page.evaluate(() => [...document.querySelector('.poster').children].map((el, i) => {
    el.dataset.fx = i; const r = el.getBoundingClientRect();
    return { i, name: el.dataset.name || '', raster: el.dataset.raster || '', txt: el.classList.contains('txt'), box: { x: r.left, y: r.top, w: r.width, h: r.height } };
  }));
  // text: blocks with .txt or data-ftext; one entry per visual line, split into styled segments
  const texts = await page.evaluate(() => {
    const res = [];
    document.querySelectorAll('.poster > .txt, .poster > [data-ftext]').forEach(block => {
      const walker = document.createTreeWalker(block, NodeFilter.SHOW_TEXT); const items = [];
      while (walker.nextNode()) {
        const node = walker.currentNode; const txt = node.textContent; if (!txt.trim()) continue;
        const cs = getComputedStyle(node.parentElement); const re = /\S+\s*/g; let m;
        while ((m = re.exec(txt))) { const r = document.createRange(); r.setStart(node, m.index); r.setEnd(node, m.index + m[0].trimEnd().length);
          const rect = r.getBoundingClientRect(); if (rect.width) items.push({ word: m[0].replace(/\u00a0/g, ' '), rect, cs }); }
      }
      const lines = [];
      items.forEach(it => { let ln = lines.find(l => Math.abs(l.t - it.rect.top) < it.rect.height * .5);
        if (!ln) { ln = { t: it.rect.top, b: it.rect.bottom, l: 1e9, segs: [], cs: it.cs }; lines.push(ln); }
        ln.l = Math.min(ln.l, it.rect.left);
        const up = it.cs.textTransform === 'uppercase';
        ln.segs.push({ text: up ? it.word.toUpperCase() : it.word, x: it.rect.left, color: it.cs.color, weight: +it.cs.fontWeight,
          family: it.cs.fontFamily.split(',')[0].replace(/["']/g, '').trim(), size: parseFloat(it.cs.fontSize),
          ls: it.cs.letterSpacing === 'normal' ? 0 : parseFloat(it.cs.letterSpacing) }); });
      lines.forEach(ln => { ln.segs.sort((a, b) => a.x - b.x);
        res.push({ block: block.dataset.name, x: ln.l, top: ln.t, h: ln.b - ln.t, segs: ln.segs }); });
    });
    return res;
  });
  const rasters = [];
  // layers whose text goes to Figma as live text are rasterised with the text made invisible
  await page.addStyleTag({ content: '[data-ftext] *, [data-ftext] { color: transparent !important; -webkit-text-stroke-color: transparent !important; }' });
  for (const L of layers) {
    if (!L.raster) continue;
    const only = await page.evaluate(i => document.querySelector(`[data-fx="${i}"]`).dataset.ftext === 'only', L.i);
    if (only) continue;
    await page.evaluate(i => { document.querySelectorAll('[data-fx]').forEach(el => el.style.display = el.dataset.fx == i ? '' : 'none');
      document.documentElement.style.background = document.body.style.background = document.querySelector('.poster').style.background = 'transparent'; }, L.i);
    let box = { x: 0, y: 0, width: W, height: H };
    if (L.raster === 'box') { const pad = 30; const b = L.box;
      const x0 = Math.max(0, Math.floor(b.x - pad)), y0 = Math.max(0, Math.floor(b.y - pad));
      const x1 = Math.min(W, Math.ceil(b.x + b.w + pad)), y1 = Math.min(H, Math.ceil(b.y + b.h + pad));
      box = { x: x0, y: y0, width: x1 - x0, height: y1 - y0 }; }
    const opaque = false;
    const file = path.join(out, String(L.i).padStart(2, '0') + (opaque ? '.jpg' : '.png'));
    await page.screenshot({ path: file, clip: box, omitBackground: !opaque, type: opaque ? 'jpeg' : 'png', quality: opaque ? 90 : undefined });
    rasters.push({ i: L.i, name: L.name, file, box, bytes: fs.statSync(file).size });
  }
  fs.writeFileSync(path.join(out, 'data.json'), JSON.stringify({ W, H, rasters, texts }, null, 1));
  console.log(rasters.map(r => `${r.i} ${r.name} ${Math.round(r.bytes / 1024)}K`).join('\n')); console.log(texts.length, 'text lines');
  await browser.close();
})();
