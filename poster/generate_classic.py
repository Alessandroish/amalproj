import math, random
OUT = '/home/user/amalproj/poster/'
W1, W2 = '#6a1515', '#4e0e0e'
CREAM = '#ece5d8'

# grid (mm)
L, M, R = (14, 100), (104, 190), (194, 283)
A, B, C = (14, 118), (122, 236), (240, 300)
art_tiles = [(M, A), (R, A), (M, B), (R, B), (M, C), (R, C), ((14, 100), (334, 392))]
def rect(x, y, fill=CREAM, extra=''):
    return f'<rect x="{x[0]}" y="{y[0]}" width="{x[1]-x[0]}" height="{y[1]-y[0]}" fill="{fill}" {extra}/>'

def spiral(cx, cy, r0, turns, d):
    pts = []
    n = 60
    for i in range(n + 1):
        t = i / n
        a = d * t * turns * 2 * math.pi
        r = r0 * (1 - .85 * t)
        pts.append((cx + d * r * math.cos(a), cy + r * math.sin(a)))
    return 'M' + ' L'.join(f'{x:.2f} {y:.2f}' for x, y in pts)

def column(cx, top, bot, w):
    h = []
    capH, baseH = w * .55, w * .45
    sx0, sx1 = cx - w / 2, cx + w / 2
    # shaft with slight entasis
    h.append(f'<path d="M{sx0+1} {top+capH} L{sx1-1} {top+capH} Q{sx1+.6} {(top+bot)/2} {sx1} {bot-baseH} L{sx0} {bot-baseH} Q{sx0-.6} {(top+bot)/2} {sx0+1} {top+capH} Z" fill="url(#cyl)"/>')
    for i in range(1, 12):
        th = -math.pi / 2 + math.pi * i / 12
        x = cx + (w / 2 - 1) * math.sin(th)
        op = .25 + .45 * (1 - math.cos(th)) / 2 + (.25 if th > .6 else 0)
        h.append(f'<line x1="{x:.2f}" y1="{top+capH+2}" x2="{x:.2f}" y2="{bot-baseH-1.5}" stroke="{W1}" stroke-width=".55" opacity="{min(op,.9):.2f}"/>')
    # capital
    aw = w * 1.55
    h.append(f'<rect x="{cx-aw/2}" y="{top}" width="{aw}" height="{w*.12}" fill="url(#cyl)" stroke="{W1}" stroke-width=".4"/>')
    h.append(f'<path d="M{cx-aw/2+2} {top+w*.12} Q{cx} {top+w*.32} {cx+aw/2-2} {top+w*.12} L{cx+aw/2-2} {top+w*.3} Q{cx} {top+w*.5} {cx-aw/2+2} {top+w*.3} Z" fill="url(#cyl)" stroke="{W1}" stroke-width=".4"/>')
    r0 = w * .2
    for d, vx in ((-1, cx - aw / 2 + r0 + .5), (1, cx + aw / 2 - r0 - .5)):
        vy = top + w * .3
        h.append(f'<circle cx="{vx}" cy="{vy}" r="{r0+.6}" fill="{CREAM}" stroke="{W1}" stroke-width=".5"/>')
        h.append(f'<path d="{spiral(vx, vy, r0, 2.4, d)}" fill="none" stroke="{W1}" stroke-width=".7"/>')
    h.append(f'<rect x="{sx0-1.5}" y="{top+capH-2.5}" width="{w+3}" height="2.5" rx="1.2" fill="url(#cyl)" stroke="{W1}" stroke-width=".35"/>')
    # base
    for k, (ww, hh) in enumerate(((w + 3, baseH * .25), (w + 7, baseH * .3), (w + 11, baseH * .45))):
        y0 = bot - baseH + sum(v for v in (baseH * .25, baseH * .3)[:k])
        h.append(f'<rect x="{cx-ww/2}" y="{y0}" width="{ww}" height="{hh}" rx="{hh/2 if k<2 else .5}" fill="url(#cyl)" stroke="{W1}" stroke-width=".35"/>')
    return '\n'.join(h)

def laurel(x0, y0, x1, y1, n=11, size=7, bend=-12):
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = x1 - x0, y1 - y0
    ln = math.hypot(dx, dy); nx, ny = -dy / ln, dx / ln
    qx, qy = mx + nx * bend, my + ny * bend
    out = [f'<path d="M{x0} {y0} Q{qx} {qy} {x1} {y1}" fill="none" stroke="{W1}" stroke-width=".9"/>']
    for i in range(1, n + 1):
        t = i / (n + 1)
        px = (1-t)**2*x0 + 2*(1-t)*t*qx + t*t*x1
        py = (1-t)**2*y0 + 2*(1-t)*t*qy + t*t*y1
        tx = 2*(1-t)*(qx-x0) + 2*t*(x1-qx); ty = 2*(1-t)*(qy-y0) + 2*t*(y1-qy)
        ang = math.degrees(math.atan2(ty, tx))
        s = size * (1 - .35 * t)
        for side in (-1, 1):
            a = ang + side * 38
            out.append(f'<g transform="translate({px:.2f} {py:.2f}) rotate({a:.1f})"><path d="M0 0 C {s*.3} {-s*.28}, {s*.8} {-s*.28}, {s} 0 C {s*.8} {s*.28}, {s*.3} {s*.28}, 0 0 Z" fill="url(#leaf)" stroke="{W1}" stroke-width=".3"/><line x1="0" y1="0" x2="{s*.9}" y2="0" stroke="{W1}" stroke-width=".25" opacity=".6"/></g>')
    out.append(f'<g transform="translate({x1} {y1}) rotate({math.degrees(math.atan2(y1-qy, x1-qx)):.1f})"><path d="M0 0 C {size*.3} {-size*.25}, {size*.8} {-size*.25}, {size} 0 C {size*.8} {size*.25}, {size*.3} {size*.25}, 0 0 Z" fill="url(#leaf)" stroke="{W1}" stroke-width=".3"/></g>')
    return '\n'.join(out)

def starburst(cx, cy, r, n=28, color=W1, sw=.35, seed=3):
    random.seed(seed)
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n + random.uniform(-.04, .04)
        rr = r * (1 if i % 4 == 0 else random.uniform(.45, .8))
        out.append(f'<line x1="{cx}" y1="{cy}" x2="{cx + rr*math.cos(a):.2f}" y2="{cy + rr*math.sin(a):.2f}" stroke="{color}" stroke-width="{sw}"/>')
    s = r * .16
    out.append(f'<path d="M{cx} {cy-s} Q{cx+s*.12} {cy-s*.12} {cx+s} {cy} Q{cx+s*.12} {cy+s*.12} {cx} {cy+s} Q{cx-s*.12} {cy+s*.12} {cx-s} {cy} Q{cx-s*.12} {cy-s*.12} {cx} {cy-s} Z" fill="{color}"/>')
    return '\n'.join(out)

def rays():
    out = []
    for (a, b, op) in ((18, 26, .55), (31, 35, .35), (40, 50, .45), (56, 60, .3)):
        ox, oy = -30, -40
        p = []
        for ang in (a, b):
            t = math.radians(ang)
            p.append((ox + 700 * math.cos(t), oy + 700 * math.sin(t)))
        out.append(f'<polygon points="{ox},{oy} {p[0][0]:.1f},{p[0][1]:.1f} {p[1][0]:.1f},{p[1][1]:.1f}" fill="url(#ray)" opacity="{op}"/>')
    return '\n'.join(out)

DEFS = f'''<defs>
<linearGradient id="cyl" x1="0" x2="1">
 <stop offset="0" stop-color="#9c5a52"/><stop offset=".18" stop-color="#e2cfc2"/><stop offset=".38" stop-color="#fbf6ee"/>
 <stop offset=".62" stop-color="#d6b8ab"/><stop offset=".85" stop-color="#8f3f37"/><stop offset="1" stop-color="{W1}"/></linearGradient>
<linearGradient id="leaf" x1="0" x2="1"><stop offset="0" stop-color="#8f3f37"/><stop offset="1" stop-color="#c79a8e"/></linearGradient>
<linearGradient id="metal" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#b9776c"/><stop offset=".5" stop-color="{W1}"/><stop offset="1" stop-color="{W2}"/></linearGradient>
<radialGradient id="glow"><stop offset="0" stop-color="#fff" stop-opacity="1"/><stop offset=".35" stop-color="#fff" stop-opacity=".6"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<linearGradient id="ray" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".9"/><stop offset=".6" stop-color="#fff" stop-opacity=".25"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<pattern id="dots" width="1.1" height="1.1" patternUnits="userSpaceOnUse" patternTransform="rotate(30)"><circle cx=".55" cy=".55" r=".22" fill="{W1}"/></pattern>
<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="4"/><feColorMatrix values="0 0 0 0 .3  0 0 0 0 .05  0 0 0 0 .05  0 0 0 .55 -.18"/></filter>
<filter id="paper" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".02 .03" numOctaves="3" seed="9"/><feColorMatrix values="0 0 0 0 .42  0 0 0 0 .08  0 0 0 0 .08  0 0 0 .5 -.1"/></filter>
<clipPath id="tiles">{''.join(rect(x, y) for x, y in art_tiles)}</clipPath>
</defs>'''

def page(cfg):
    tiles = ''.join(rect(x, y) for x, y in art_tiles) + rect(L, B) + rect(L, (240, 330))
    svg = f'''<svg class="art" viewBox="0 0 297 420">{DEFS}
{tiles}
<g clip-path="url(#tiles)">
 <rect width="297" height="420" filter="url(#paper)" opacity=".5"/>
 {cfg['art']}
 {rays()}
 <rect width="297" height="420" fill="url(#dots)" opacity=".07"/>
</g>
<g transform="translate(57 278)">{starburst(0, 0, 28, seed=cfg['seed'])}</g>
<rect width="297" height="420" filter="url(#grain)" opacity=".5"/>
</svg>'''
    html = f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><title>{cfg['title']}</title>
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600&family=Cormorant+Garamond:ital,wght@1,500;1,600&family=Montserrat:wght@800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="classic.css"></head>
<body><div class="poster">
{svg}
<div class="box" style="left:14mm; top:14mm; width:86mm; height:104mm;"><div class="big" data-fit data-h="{cfg.get('toph',104)}" data-top="{cfg.get('topoff',0)}">{cfg['top']}</div></div>
<div class="box date" style="right:18mm; top:20mm;">28<br>11<br>26<small>13:25</small></div>
<div class="box text" style="left:14mm; top:122mm; width:86mm; height:114mm;">
  <div class="kind">{cfg['kind']}</div>
  <h3>{cfg['head']}</h3>
  <p>{cfg['desc']}</p>
  <div class="tags">{cfg['tags']}</div>
</div>
<div class="place" style="left:14mm; width:86mm; top:313mm;"><span>аудитория</span><b>609</b></div>
<div class="box" style="left:108mm; top:306mm; width:171mm;">
  <div class="small-word">{cfg['small']}</div>
  <div style="width:171mm"><div class="big" data-fit data-h="{cfg['bigh']}">{cfg['bottom']}</div></div>
</div>
<div class="foot">{cfg['kind']} / Регистрация: 6 этаж, 603 кабинет<br>Сб 28 ноября 2026 &nbsp;•&nbsp; 13:25 &nbsp;•&nbsp; 609 аудитория</div>
</div>
<script src="classic-fit.js"></script>
</body></html>'''
    open(OUT + cfg['file'], 'w').write(html)

# ---------- law ----------
law_art = column(190, 76, 300, 36) + f'''
<g>
 <rect x="188.6" y="44" width="2.8" height="32" fill="url(#metal)"/>
 <circle cx="190" cy="42" r="4.2" fill="url(#metal)"/>
 <path d="M136 64.5 L244 59.5 L244 62.5 L136 67.5 Z" fill="url(#metal)"/>
 <circle cx="136" cy="66" r="2.6" fill="url(#metal)"/><circle cx="244" cy="61" r="2.6" fill="url(#metal)"/>
 <g stroke="{W2}" stroke-width=".55" fill="none">
  <path d="M136 66 L116 152 M136 66 L156 152 M136 66 L136 152"/>
  <path d="M244 61 L224 140 M244 61 L264 140 M244 61 L244 140"/>
 </g>
 <path d="M112 152 Q136 172 160 152 Z" fill="url(#metal)"/>
 <path d="M220 140 Q244 160 268 140 Z" fill="url(#metal)"/>
</g>
{laurel(22, 384, 92, 344, n=9, size=9, bend=-10)}'''
page(dict(file='poster-law-classic.html', title='Знай свои права', art=law_art, seed=3,
  top='Знай', toph=80, topoff=22, small='свои', bottom='Права', bigh=60,
  kind='Мастер-класс',
  head='Основы трудового права для успешного трудоустройства',
  desc='Юридические аспекты трудовых отношений с&nbsp;работодателем, на которые важно обратить внимание.',
  tags='КЕЙСЫ / ПРАКТИКА / ПРАВО'))

# ---------- networking ----------
arch_cx, arch_r, arch_y = 210, 50, 122
net_art = column(160, arch_y, 300, 28) + column(260, arch_y, 300, 28) + f'''
<path d="M{arch_cx-arch_r-8} {arch_y} A {arch_r+8} {arch_r+8} 0 0 1 {arch_cx+arch_r+8} {arch_y} L{arch_cx+arch_r-4} {arch_y} A {arch_r-4} {arch_r-4} 0 0 0 {arch_cx-arch_r+4} {arch_y} Z" fill="url(#cyl)" stroke="{W1}" stroke-width=".5"/>
''' + '\n'.join(
  f'<line x1="{arch_cx+(arch_r-4)*math.cos(math.pi+math.pi*i/13):.2f}" y1="{arch_y+(arch_r-4)*math.sin(math.pi+math.pi*i/13):.2f}" x2="{arch_cx+(arch_r+8)*math.cos(math.pi+math.pi*i/13):.2f}" y2="{arch_y+(arch_r+8)*math.sin(math.pi+math.pi*i/13):.2f}" stroke="{W1}" stroke-width=".45"/>'
  for i in range(1, 13)) + f'''
<path d="M{arch_cx-6} {arch_y-arch_r-10} L{arch_cx+6} {arch_y-arch_r-10} L{arch_cx+4.5} {arch_y-arch_r+5} L{arch_cx-4.5} {arch_y-arch_r+5} Z" fill="{CREAM}" stroke="{W1}" stroke-width=".6"/>
<circle cx="{arch_cx}" cy="{arch_y-arch_r-2}" r="30" fill="url(#glow)"/>
<g>{starburst(arch_cx, arch_y-arch_r-2, 26, n=32, color=W1, sw=.3, seed=8)}</g>
{laurel(22, 384, 92, 344, n=9, size=9, bend=-10)}'''
page(dict(file='poster-networking-classic.html', title='Твоя точка коннекта', art=net_art, seed=5,
  top='Твоя', toph=96, topoff=4, small='точка', bottom='Коннекта', bigh=60,
  kind='Деловая игра',
  head='The Hustle Hub:<br>Networking Quest',
  desc='Прокачай коммуникацию с&nbsp;разными партнёрами и&nbsp;найди идеальное совпадение для сотрудничества. Игровой формат с&nbsp;юмором — без языкового барьера.',
  tags='ИГРА / СВЯЗИ / ПРАКТИКА'))
print('ok')
