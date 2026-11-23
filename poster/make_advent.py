"""Assets for the advent-calendar poster: stained red wood texture and a lit Christmas tree.
Usage: python3 make_advent.py <outdir>"""
import sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

out = sys.argv[1]
rng = np.random.default_rng(2027)


def blur_x(a, r):
    c = np.cumsum(np.pad(a, ((0, 0), (r + 1, r)), mode='wrap'), axis=1)
    return (c[:, 2 * r + 1:] - c[:, :-2 * r - 1]) / (2 * r + 1)


def blur_y(a, r):
    return blur_x(a.T, r).T


# ---------- wood ----------
H, W = 2520, 1782
n1 = blur_y(blur_x(rng.standard_normal((H, W)), 260), 2)
n1 = n1 / n1.std()
n2 = blur_y(blur_x(rng.standard_normal((H, W)), 60), 1)
n2 = n2 / n2.std()
low = blur_y(blur_x(rng.standard_normal((H, W)), 400), 40)
low = low / low.std()
yy = np.arange(H)[:, None].astype(np.float64)
rings = np.sin(yy * .09 + low * 6 + n1 * 1.2)
grain = .55 * n1 + .35 * n2 + .45 * np.sign(rings) * np.abs(rings) ** 3
fine = blur_x(rng.standard_normal((H, W)), 8)
fine = fine / fine.std()
v = 1 + .10 * grain + .035 * fine + .06 * low
base = np.array([112, 26, 28], np.float64) / 255
img = np.clip(base[None, None, :] * v[..., None], 0, 1)
# darker streaks
img *= (1 - .18 * np.clip(rings - .6, 0, 1))[..., None]
import os
if not os.path.exists(f'{out}/wood.jpg'): Image.fromarray((img * 255).astype(np.uint8)).save(f'{out}/wood.jpg', quality=90)
print('wood ok')

# ---------- tree ----------
TW, TH = 1500, 2000
cx = TW / 2
top, bot = 170, 1880
tree = Image.new('RGBA', (TW, TH), (0, 0, 0, 0))
d = ImageDraw.Draw(tree)


def halfw(y):
    t = (y - top) / (bot - top)
    return 30 + t * 640


# trunk
d.polygon([(cx - 26, bot - 120), (cx + 26, bot - 120), (cx + 34, bot + 60), (cx - 34, bot + 60)], fill=(58, 34, 20, 255))
# dark interior so gaps between branches read as depth, not holes
cone = Image.new('L', (TW, TH), 0)
ImageDraw.Draw(cone).polygon([(cx, top + 40), (cx + halfw(bot - 60) * .66, bot - 90), (cx - halfw(bot - 60) * .66, bot - 90)], fill=255)
cone = cone.filter(ImageFilter.GaussianBlur(40))
dark = Image.new('RGBA', (TW, TH), (8, 22, 14, 255)); dark.putalpha(cone)
tree.alpha_composite(dark)
tiers = 34
for depth in (0, 1, 2):          # back (dark) -> front (light)
    for k in range(tiers):
        y0 = top + (bot - top - 80) * (k / tiers) ** .92 + 20
        w = halfw(y0 + 60)
        nb = int(10 + 26 * k / tiers)
        for b in range(nb):
            s = rng.uniform(-1, 1)
            if depth == 2 and abs(s) < .25 and rng.random() < .5:
                s *= 2.5
            ex = cx + s * w * rng.uniform(.75, 1.05)
            ey = y0 + abs(s) * 60 + rng.uniform(10, 70) + depth * 6
            sx = cx + s * 20
            steps = 18
            for i in range(steps):
                t = i / steps
                px = sx + (ex - sx) * t
                py = y0 + (ey - y0) * t + math.sin(t * math.pi) * -10
                for _ in range(5):
                    a = math.atan2(ey - y0, ex - sx) + rng.uniform(-1.4, 1.4)
                    L = rng.uniform(12, 26) * (1 - .35 * (1 - t))
                    shade = [(14, 44, 26), (24, 70, 38), (40, 98, 52)][depth]
                    jitter = rng.uniform(.75, 1.25)
                    tip = t > .7 and depth == 2
                    col = tuple(int(min(255, c * jitter * (1.35 if tip else 1))) for c in shade) + (255,)
                    d.line([(px, py), (px + math.cos(a) * L, py + math.sin(a) * L)], fill=col, width=int(rng.choice([2, 2, 3])))
print('needles ok')
T = np.asarray(tree).astype(np.float64) / 255
alpha = T[..., 3:4]
# shading: darker at edges and bottom-left, lit from front-centre
xx = (np.arange(TW)[None, :] - cx) / 700
ys = (np.arange(TH)[:, None] - top) / (bot - top)
light = np.clip(1.05 - .5 * np.abs(xx) - .2 * ys + .18 * np.clip(-xx, 0, 1), .38, 1.15)
rgb = T[..., :3] * light[..., None]


def glow_layer(points, color, rad, blur):
    g = Image.new('L', (TW, TH), 0)
    gd = ImageDraw.Draw(g)
    for (x, y, r) in points:
        gd.ellipse([x - r * rad, y - r * rad, x + r * rad, y + r * rad], fill=255)
    g = g.filter(ImageFilter.GaussianBlur(blur))
    return (np.asarray(g).astype(np.float64) / 255)[..., None] * np.array(color)[None, None, :]


# fairy lights inside the cone
pts = []
for i in range(240):
    y = rng.uniform(top + 60, bot - 90)
    x = cx + rng.uniform(-1, 1) * halfw(y) * .92
    pts.append((x, y, rng.uniform(.8, 1.4)))
glow = glow_layer(pts, [1.0, .62, .28], 16, 22) * .55 + glow_layer(pts, [1, .9, .7], 3.5, 2) * 1.3
rgb = rgb + glow
alpha = np.maximum(alpha, np.clip(glow.max(axis=2, keepdims=True) * .9, 0, 1))
im = Image.fromarray((np.dstack([np.clip(rgb, 0, 1), np.clip(alpha, 0, 1)]) * 255).astype(np.uint8), 'RGBA')


def ball(r, col):
    s = int(r * 2 + 4)
    yy, xx = np.mgrid[0:s, 0:s].astype(np.float64)
    dx, dy = (xx - s / 2) / r, (yy - s / 2) / r
    rr = np.sqrt(dx * dx + dy * dy)
    z = np.sqrt(np.clip(1 - rr * rr, 0, 1))
    lam = np.clip(-.35 * dx - .45 * dy + .8 * z, 0, 1)
    c = np.array(col) / 255
    rgb = c[None, None, :] * (.25 + .9 * lam[..., None])
    spec = np.exp(-((dx + .38) ** 2 + (dy + .42) ** 2) / .02)
    rgb = rgb + spec[..., None] * .95 + np.exp(-((dx - .3) ** 2 + (dy - .45) ** 2) / .03)[..., None] * np.array([1, .8, .5]) * .45
    a = np.clip((1 - rr) * r, 0, 1)
    return Image.fromarray((np.dstack([np.clip(rgb, 0, 1), a]) * 255).astype(np.uint8), 'RGBA')


# garland swags of gold beads
gd = ImageDraw.Draw(im)
for k, yb in enumerate(np.linspace(top + 260, bot - 220, 6)):
    w = halfw(yb)
    for i in range(70):
        t = i / 69
        x = cx - w * .9 + 2 * w * .9 * t
        y = yb + math.sin(t * math.pi) * 70 - (t - .5) * 60 * (1 if k % 2 else -1)
        if abs(x - cx) > halfw(y) * .95:
            continue
        b = ball(5.5, (220, 170, 70))
        im.alpha_composite(b, (int(x - b.width / 2), int(y - b.height / 2)))
# ornaments
cols = [(200, 20, 30), (210, 160, 60), (190, 25, 40), (230, 190, 90), (160, 10, 25)]
disco = Image.open(f'{out}/discoball.png').convert('RGBA')
placed = []
for i in range(46):
    for _ in range(40):
        y = rng.uniform(top + 160, bot - 120)
        x = cx + rng.uniform(-1, 1) * halfw(y) * .85
        r = rng.uniform(17, 30) * (.7 + .5 * (y - top) / (bot - top))
        if all((x - px) ** 2 + (y - py) ** 2 > (r + pr + 14) ** 2 for px, py, pr in placed):
            break
    placed.append((x, y, r))
    if i % 7 == 3:
        b = disco.resize((int(r * 2.2), int(r * 2.2)), Image.LANCZOS)
    else:
        b = ball(r, cols[i % len(cols)])
    gd.line([(x, y - r - 10), (x, y - r)], fill=(200, 170, 90, 255), width=2)
    im.alpha_composite(b, (int(x - b.width / 2), int(y - b.height / 2)))
# front needle tips over the ornaments (they sit inside the branches)
fd = ImageDraw.Draw(im)
for k in range(2600):
    y = rng.uniform(top + 80, bot - 70)
    x = cx + rng.uniform(-1, 1) * halfw(y) * .95
    a = rng.uniform(0, math.pi) + .2
    L = rng.uniform(10, 22)
    g = rng.uniform(.8, 1.3)
    fd.line([(x, y), (x + math.cos(a) * L, y + math.sin(a) * L)], fill=(int(34 * g), int(86 * g), int(46 * g), 255), width=2)
# a touch of desaturation + warm ambient so the tree sits in the warm niche
A = np.asarray(im).astype(np.float64) / 255
lum = A[..., :3].mean(axis=2, keepdims=True)
A[..., :3] = (A[..., :3] * .85 + lum * .15) * np.array([1.04, 1.0, .9])
im = Image.fromarray((np.clip(A, 0, 1) * 255).astype(np.uint8), 'RGBA')
gd = ImageDraw.Draw(im)
# star on top
star = Image.new('RGBA', (TW, TH), (0, 0, 0, 0))
sd = ImageDraw.Draw(star)
sp = []
for i in range(10):
    a = -math.pi / 2 + i * math.pi / 5
    R = 95 if i % 2 == 0 else 40
    sp.append((cx + math.cos(a) * R, top - 30 + math.sin(a) * R))
sd.polygon(sp, fill=(255, 205, 90, 255))
sg = star.filter(ImageFilter.GaussianBlur(30))
im.alpha_composite(sg)
im.alpha_composite(sg)
im.alpha_composite(star)
# highlight facet on star
sd2 = ImageDraw.Draw(im)
sd2.polygon([(cx, top - 125), (cx + 16, top - 40), (cx, top - 30)], fill=(255, 245, 200, 255))
im.save(f'{out}/tree.png', optimize=True)
print('tree ok', im.size)
