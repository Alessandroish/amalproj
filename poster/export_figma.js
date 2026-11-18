// Export an HTML poster to a layered SVG that Figma imports (File → Import, or drag & drop).
// Rasters: paper, torn band, statue, shades, wear, huge stretched titles. Editable text: everything else.
// Usage: node export_figma.js poster-law-halftone   ->  poster-law-halftone.figma.svg
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const name = process.argv[2] || 'poster-law-halftone';
const W = 1123, H = 1587, S = 2;

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: S });
  await page.goto('file://' + path.resolve(name + '.html'), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);

  // tag every top-level layer of the poster
  const layers = await page.evaluate(() => {
    const kids = [...document.querySelector('.poster').children];
    return kids.map((el, i) => { el.dataset.fx = i; return { i, tag: el.tagName.toLowerCase(), cls: el.getAttribute('class') || '', id: el.id || '', name: el.dataset.name || '', raster: el.dataset.raster || '' }; });
  });

  async function shot(i, full, opaque) {
    await page.evaluate(([i]) => {
      document.querySelectorAll('[data-fx]').forEach(el => el.style.display = el.dataset.fx == i ? '' : 'none');
      document.documentElement.style.background = document.body.style.background = document.querySelector('.poster').style.background = 'transparent';
    }, [i]);
    const opts = { omitBackground: !opaque, type: opaque ? 'jpeg' : 'png' };
    if (opaque) opts.quality = 92;
    let box = { x: 0, y: 0, width: W, height: H };
    if (!full) {
      box = await page.evaluate(i => { const r = document.querySelector(`[data-fx="${i}"]`).getBoundingClientRect(); return { x: r.left, y: r.top, width: r.width, height: r.height }; }, i);
      box = { x: Math.max(0, Math.floor(box.x) - 2), y: Math.max(0, Math.floor(box.y) - 2), width: Math.ceil(box.width) + 4, height: Math.ceil(box.height) + 4 };
      box.width = Math.min(box.width, W - box.x); box.height = Math.min(box.height, H - box.y);
    }
    opts.clip = box;
    const buf = await page.screenshot(opts);
    return { box, href: `data:image/${opaque ? 'jpeg' : 'png'};base64,${buf.toString('base64')}` };
  }

  // CSS-generated quotes (<q>) are not text nodes: write them into the text, same glyphs, same layout
  await page.evaluate(() => document.querySelectorAll('q').forEach(q => { q.style.quotes = 'none'; q.textContent = '«' + q.textContent + '»'; }));

  // editable text: split each text block into visual lines with their computed style
  const texts = await page.evaluate(() => {
    const metrics = { 'Montserrat': [968, 251], 'Playfair Display': [1082, 251] };
    const out = [];
    const blocks = document.querySelectorAll('.top, .right, .left, .cite, .reg, .credit, .txt');
    blocks.forEach(block => {
      const walker = document.createTreeWalker(block, NodeFilter.SHOW_TEXT);
      const items = [];
      while (walker.nextNode()) {
        const node = walker.currentNode; const txt = node.textContent;
        if (!txt.trim()) continue;
        const cs = getComputedStyle(node.parentElement);
        const re = /\S+\s*/g; let m;
        while ((m = re.exec(txt))) {
          const r = document.createRange(); r.setStart(node, m.index); r.setEnd(node, m.index + m[0].trimEnd().length);
          const rect = r.getBoundingClientRect(); if (!rect.width) continue;
          items.push({ word: m[0], rect, cs, quoted: node.parentElement.tagName === 'Q' });
        }
      }
      // group into lines by top & style
      const lines = [];
      items.forEach(it => {
        const key = `${Math.round(it.rect.top)}|${it.cs.fontSize}|${it.cs.fontWeight}|${it.cs.color}|${it.cs.fontStyle}`;
        let ln = lines.find(l => l.key === key);
        if (!ln) { ln = { key, words: [], rect: { l: 1e9, t: it.rect.top, b: it.rect.bottom }, cs: it.cs }; lines.push(ln); }
        ln.words.push(it.word); ln.rect.l = Math.min(ln.rect.l, it.rect.left);
      });
      lines.forEach(ln => {
        const cs = ln.cs; const fam = cs.fontFamily.split(',')[0].replace(/["']/g, '').trim();
        const [a, d] = metrics[fam] || [950, 250];
        const h = ln.rect.b - ln.rect.t;
        let text = ln.words.join('').trimEnd();
        if (cs.textTransform === 'uppercase') text = text.toUpperCase();
        out.push({ text, x: ln.rect.l, y: ln.rect.t + h * a / (a + d), family: fam, size: parseFloat(cs.fontSize), weight: cs.fontWeight,
                   style: cs.fontStyle, fill: cs.color, ls: cs.letterSpacing === 'normal' ? 0 : parseFloat(cs.letterSpacing), block: block.dataset.name || block.className });
      });
    });
    return out;
  });

  // vector stars and icons
  const vectors = await page.evaluate(() => [...document.querySelectorAll('.poster > svg.star, .reg svg')].map(s => {
    const r = s.getBoundingClientRect();
    return { x: r.left, y: r.top, w: r.width, h: r.height, vb: s.getAttribute('viewBox'), inner: s.innerHTML, id: s.id || '' };
  }));

  const esc = t => t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const parts = [];
  const raster = async (i, label, full, opaque) => { const { box, href } = await shot(i, full, opaque);
    parts.push(`<g id="${label}"><image x="${box.x}" y="${box.y}" width="${box.width}" height="${box.height}" href="${href}"/></g>`); };

  for (const L of layers) {
    // generic posters: <… data-name="Слой" data-raster="full|box"> marks a raster layer
    if (L.raster) await raster(L.i, L.name || ('Слой ' + L.i), L.raster === 'full', L.i === 0);
    else if (L.cls === 'layer' && L.i === 0) await raster(L.i, 'Бумага', true, true);
    else if (L.id === 't1') await raster(L.i, 'Заголовок ПРАВО', false);
    else if (L.id === 'torn') await raster(L.i, 'Рваный край и красные фигуры', true);
    else if (L.cls === 'statue') await raster(L.i, 'Статуя растр', true);
    else if (L.id === 't2a') await raster(L.i, 'Заголовок НА', false);
    else if (L.id === 't2b') await raster(L.i, 'Заголовок ТРУД', false);
    else if (L.tag === 'svg' && L.cls === 'layer') await raster(L.i, L.i < 8 ? 'Затемнение низа' : 'Потёртость печати', true);
  }
  parts.push('<g id="Звёзды">' + vectors.filter(v => !v.inner.includes('circle')).map(v =>
    `<svg x="${v.x.toFixed(1)}" y="${v.y.toFixed(1)}" width="${v.w.toFixed(1)}" height="${v.h.toFixed(1)}" viewBox="${v.vb}">${v.inner}</svg>`).join('') + '</g>');
  parts.push('<g id="Иконка геометки">' + vectors.filter(v => v.inner.includes('circle')).map(v =>
    `<svg x="${v.x.toFixed(1)}" y="${v.y.toFixed(1)}" width="${v.w.toFixed(1)}" height="${v.h.toFixed(1)}" viewBox="${v.vb}">${v.inner}</svg>`).join('') + '</g>');

  const groups = {};
  texts.forEach(t => (groups[t.block] = groups[t.block] || []).push(t));
  const gname = { top: 'Текст: шапка', right: 'Текст: дата', left: 'Текст: фраза', cite: 'Текст: ст. 37', reg: 'Текст: регистрация', credit: 'Текст: подпись фото' };
  for (const [b, arr] of Object.entries(groups)) {
    parts.push(`<g id="${gname[b] || b}">` + arr.map(t =>
      `<text x="${t.x.toFixed(1)}" y="${t.y.toFixed(1)}" font-family="${t.family}" font-size="${t.size.toFixed(2)}" font-weight="${t.weight}"${t.style === 'italic' ? ' font-style="italic"' : ''}${t.ls ? ` letter-spacing="${t.ls.toFixed(2)}"` : ''} fill="${t.fill}">${esc(t.text)}</text>`).join('') + '</g>');
  }

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">\n` +
    `<g id="${name} (A3)">\n${parts.join('\n')}\n</g>\n</svg>\n`;
  fs.writeFileSync(name + '.figma.svg', svg);
  console.log(name + '.figma.svg', (svg.length / 1e6).toFixed(1) + ' MB', texts.length, 'text lines');
  await browser.close();
})();
