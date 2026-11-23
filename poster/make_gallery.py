"""Assets for the 'gallery' poster: carved gold frame, oil-painting scenes, white plaster wall.
Usage: python3 make_gallery.py <dir>   (expects discoball.png, tree.png, mic.png, boombox.png in <dir>)"""
import sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

D = sys.argv[1]
rng = np.random.default_rng(1999)


def _box(a, r, ax):
    r = max(1, int(r))
    a = np.moveaxis(a, ax, -1)
    c = np.cumsum(np.pad(a, [(0, 0)] * (a.ndim - 1) + [(r + 1, r)], mode='reflect'), axis=-1)
    return np.moveaxis((c[..., 2 * r + 1:] - c[..., :-2 * r - 1]) / (2 * r + 1), -1, ax)


def blur(a, r):
    r = max(1, r * .58)
    for _ in range(3):
        a = _box(_box(a, r, 0), r, 1)
    return a


# ---------------- plaster wall ----------------
W, H = 1782, 2520
n = rng.standard_normal((H, W))
low = blur(rng.standard_normal((H, W)), 90); low /= low.std()
mid = blur(n, 6); mid /= mid.std()
streak = blur(blur(rng.standard_normal((H, W)), 3), 30)
streak = _box(streak, 80, 1); streak /= streak.std()
v = .93 + .018 * low + .012 * mid + .015 * streak + .01 * blur(n, 1)
yy, xx = np.mgrid[0:H, 0:W]
v = v * np.clip(1.04 - .22 * np.hypot((xx - W * .5) / W, (yy - H * .45) / H) ** 1.8, .8, 1.04)
img = np.clip(np.dstack([v * .985, v * .98, v * .975]), 0, 1)
Image.fromarray((img * 255).astype(np.uint8)).save(f'{D}/plaster.jpg', quality=90)
print('plaster ok')


# ---------------- carved gold frame ----------------
def gold_frame(w, h, b, seed=0, scale=1.0):
    r = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
    d = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy))   # distance from the outer edge
    t = d / b                                                                 # 0 outer .. 1 inner
    horiz = np.minimum(yy, h - 1 - yy) < np.minimum(xx, w - 1 - xx)
    s = np.where(horiz, xx, yy) / (b * .75)                                    # along-edge coordinate
    def bump(c, wdt, amp):
        return amp * np.clip(1 - ((t - c) / wdt) ** 2, 0, 1) ** .6
    hgt = bump(.08, .08, 1.0) + bump(.24, .09, .55) - bump(.36, .06, .35)      # outer lip, round, cove
    orn = np.clip(1 - ((t - .58) / .16) ** 2, 0, 1)                           # ornament band
    leaf = (np.sin(s * math.pi * 2) * .5 + .5) ** 2 * np.sin(np.clip((t - .42) / .32, 0, 1) * math.pi)
    curl = np.sin(s * math.pi * 4 + np.sin(s * math.pi * 2) * 2 + t * 9) * .5 + .5
    hgt += orn * (.4 + .55 * leaf) * (.7 + .3 * curl)
    hgt += bump(.84, .05, .6) + bump(.93, .035, .45)                         # inner beads
    beads = (np.sin(s * math.pi * 6) * .5 + .5) ** 3
    hgt += np.clip(1 - ((t - .84) / .05) ** 2, 0, 1) * beads * .25
    hgt += .03 * blur(r.standard_normal((h, w)), 2.5)
    hgt = np.where(t > 1, -.4, hgt)
    gy, gx = np.gradient(blur(hgt, 1.5) * b * .11 * scale)
    nx, ny, nz = -gx, -gy, np.ones_like(hgt)
    ln = np.sqrt(nx * nx + ny * ny + nz * nz); nx /= ln; ny /= ln; nz /= ln
    L = np.array([-.5, -.55, .67]); L /= np.linalg.norm(L)
    lam = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    Hh = L + np.array([0, 0, 1]); Hh /= np.linalg.norm(Hh)
    spec = np.clip(nx * Hh[0] + ny * Hh[1] + nz * Hh[2], 0, 1) ** 40
    ao = np.clip(.75 + .9 * (hgt - blur(hgt, b * .06)), .45, 1.08)
    dark = np.array([.30, .18, .06]); midc = np.array([.78, .58, .26]); hi = np.array([1.0, .9, .62])
    k = lam[..., None]
    col = np.where(k < .6, dark + (midc - dark) * (k / .6), midc + (hi - midc) * ((k - .6) / .4))
    col = col * ao[..., None] + spec[..., None] * np.array([1, .95, .8]) * .9
    col *= (1 + .08 * blur(r.standard_normal((h, w)), 6))[..., None]           # patina
    a = (t <= 1).astype(np.float64)
    inner_sh = np.clip(1 - (t - 1) / .25, 0, 1) * (t > 1)                     # shadow the frame casts on the canvas
    rgba = np.dstack([np.clip(col, 0, 1), a])
    sh = np.dstack([np.zeros((h, w, 3)), inner_sh * .55])
    rgba = np.where((t > 1)[..., None], sh, rgba)
    return Image.fromarray((rgba * 255).astype(np.uint8), 'RGBA')


gold_frame(1500, 1700, 190, 1).save(f'{D}/gframe-main.png', optimize=True)
gold_frame(700, 1000, 110, 2, .8).save(f'{D}/gframe-side.png', optimize=True)
print('frames ok')


# ---------------- oil painting look ----------------
def oil(im, strength=1.0):
    im = im.convert('RGB')
    w, h = im.size
    im = im.filter(ImageFilter.ModeFilter(5)).filter(ImageFilter.SMOOTH_MORE)
    a = np.asarray(im).astype(np.float64) / 255
    # brush strokes: directional noise modulating value + palette-knife highlights
    n = rng.standard_normal((h, w))
    strokes = _box(_box(n, 9, 1), 2, 0); strokes /= strokes.std()
    strokes2 = _box(_box(n, 2, 1), 9, 0); strokes2 /= strokes2.std()
    lum = a.mean(axis=2)
    fld = blur(rng.standard_normal((h, w)), 60); fld = fld / fld.std()
    st = np.where(fld > 0, strokes, strokes2)
    a = a * (1 + .035 * strength * st[..., None])
    # warm varnish, crackle-free canvas weave
    weave = (np.sin(np.arange(w)[None, :] * 1.3) * np.sin(np.arange(h)[:, None] * 1.3)) * .015
    a = a * np.array([1.06, .99, .86]) + weave[..., None]
    a = .03 + a * .97
    vig = np.clip(1.1 - .75 * np.hypot((np.arange(w)[None, :] - w / 2) / w, (np.arange(h)[:, None] - h / 2) / h) ** 1.4, .4, 1)
    return Image.fromarray((np.clip(a * vig[..., None], 0, 1) * 255).astype(np.uint8))


def glow(size, cx, cy, r, col, alpha):
    g = Image.new('RGBA', size, (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col + (alpha,))
    return g.filter(ImageFilter.GaussianBlur(r * .6))


ball = Image.open(f'{D}/discoball.png').convert('RGBA')
tree = Image.open(f'{D}/tree.png').convert('RGBA')
mic = Image.open(f'{D}/mic.png').convert('RGBA')
bb = Image.open(f'{D}/boombox.png').convert('RGBA')

# main painting: dark stone hall, glowing arch, disco ball hanging in the light, spots on the walls, boombox on the floor
PW, PH = 1100, 1300
yy, xx = np.mgrid[0:PH, 0:PW].astype(np.float64)
stone = blur(rng.standard_normal((PH, PW)), 26); stone /= stone.std()
cx_, R_, ay0, ay1 = 730, 190, 260, 1020
glowr = np.exp(-(((xx - cx_) / 380) ** 2 + ((yy - 620) / 520) ** 2))
wall = np.dstack([.18 + .55 * glowr, .11 + .40 * glowr, .06 + .22 * glowr]) * (1 + .05 * stone)[..., None]
inarch = (((xx > cx_ - R_) & (xx < cx_ + R_) & (yy > ay0 + R_)) | (np.hypot(xx - cx_, yy - (ay0 + R_)) < R_)) & (yy < ay1)
jamb = inarch & ((np.hypot(xx - cx_ - 40, np.maximum(yy - (ay0 + R_) - 30, 0) * 0 + np.minimum(yy - (ay0 + R_) - 30, 0)) > R_ - 10) | (xx < cx_ - R_ + 50)) & (xx < cx_ - 40)
core = np.exp(-(((xx - cx_ - 20) / 120) ** 2 + ((yy - 640) / 400) ** 2))
archc = np.dstack([.98 + 0 * xx, .82 + .14 * core, .52 + .34 * core])
img = np.where(inarch[..., None], archc, wall)
img = np.where(jamb[..., None], np.dstack([.55 + .2 * glowr, .38 + .15 * glowr, .2 + .08 * glowr]), img)
floor = yy > ay1
pool = np.exp(-(((xx - cx_ + (yy - ay1) * .5) / np.maximum(180 + (yy - ay1) * .9, 60)) ** 2)) * np.clip(1 - (yy - ay1) / 320, 0, 1)
fl = np.dstack([.2 + .7 * pool, .13 + .55 * pool, .07 + .3 * pool]) * (1 + .04 * stone)[..., None]
img = np.where(floor[..., None], fl, img)
p = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
p.alpha_composite(glow((PW, PH), cx_, 600, 340, (255, 214, 150), 130))
for i in range(80):
    x, y = int(rng.uniform(40, PW - 40)), int(rng.uniform(60, 980))
    if abs(x - cx_) < R_ + 30 and y > ay0 - 20: continue
    r = int(rng.uniform(5, 12)); c = [(255, 196, 228), (196, 238, 255), (255, 226, 170), (255, 250, 240)][i % 4]
    p.alpha_composite(glow((PW, PH), x, y, r, c, 210))
d = ImageDraw.Draw(p)
d.line([(cx_, 0), (cx_, 270)], fill=(190, 160, 110, 255), width=3)
p.alpha_composite(glow((PW, PH), cx_, 400, 190, (255, 150, 215), 110))
p.alpha_composite(ball.resize((260, 260), Image.LANCZOS), (cx_ - 130, 270))
sh = Image.new('RGBA', (PW, PH), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([200, 1120, 560, 1170], fill=(0, 0, 0, 170))
p.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
p.alpha_composite(bb.resize((400, 261), Image.LANCZOS), (180, 900))
oil(p).save(f'{D}/paint-main.jpg', quality=90)

# side paintings
def scene(fg, box, bgc, lightc, size=(800, 800)):
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w]
    st = blur(rng.standard_normal((h, w)), 10); st /= st.std()
    l = np.exp(-(((xx - w * .55) / (w * .45)) ** 2 + ((yy - h * .4) / (h * .5)) ** 2))
    a = np.dstack([bgc[i] * (1 + .05 * st) + lightc[i] * l for i in range(3)])
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
    im.alpha_composite(fg.resize((box[2], box[3]), Image.LANCZOS), (box[0], box[1]))
    return oil(im)


scene(tree, (120, 60, 560, 746), (.12, .06, .03), (.55, .32, .12)).save(f'{D}/paint-tree.jpg', quality=90)
scene(mic, (300, 40, 230, 744), (.10, .03, .03), (.6, .3, .15)).save(f'{D}/paint-mic.jpg', quality=90)
scene(ball, (190, 170, 420, 420), (.08, .04, .1), (.45, .25, .4)).save(f'{D}/paint-ball.jpg', quality=90)
print('paintings ok')
scene(bb, (60, 230, 680, 444), (.1, .05, .03), (.5, .3, .15)).save(f'{D}/paint-bb.jpg', quality=90)
oil(Image.open(f'{D}/board-neon90.jpg').resize((800, 800)), .6).save(f'{D}/paint-neon.jpg', quality=90)
print('extra ok')
