"""Assets for the 'detective board' poster: concrete wall + polaroid photos built from our own renders/props.
Usage: python3 make_board.py <dir>   (expects discoball.png, boombox.png, mic.png, tree.png, wood.jpg and the
poster-ny-disco90*.png renders in <dir>)"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

D = sys.argv[1]
rng = np.random.default_rng(42)


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


# ---------- concrete wall ----------
W, H = 1782, 2520
n = rng.standard_normal((H, W))
low = blur(rng.standard_normal((H, W)), 120); low /= low.std()
mid = blur(n, 14); mid /= mid.std()
fine = blur(n, 1.2); fine /= fine.std()
pits = (blur(rng.standard_normal((H, W)), 2) > 2.2).astype(float)
v = .72 + .03 * low + .016 * mid + .022 * fine - .08 * blur(pits, .8)
yy, xx = np.mgrid[0:H, 0:W]
r = np.hypot((xx - W * .5) / W, (yy - H * .47) / H)
v = v * np.clip(1.12 - 1.25 * r ** 1.6, .35, 1.1)
img = np.clip(np.dstack([v * .98, v * .98, v]), 0, 1)
Image.fromarray((img * 255).astype(np.uint8)).save(f'{D}/concrete.jpg', quality=90)
print('concrete ok')


# ---------- photos ----------
def grade(im, warm=1.0):
    im = im.convert('RGB').resize((640, 640), Image.LANCZOS)
    a = np.asarray(im).astype(np.float64) / 255
    a = a * np.array([1.04 * warm, 1.0, .94 / warm])
    a = .06 + a * .9                                     # lifted blacks, like printed film
    yy, xx = np.mgrid[0:640, 0:640]
    vig = np.clip(1.15 - .9 * np.hypot((xx - 320) / 640, (yy - 320) / 640) ** 1.5, .45, 1)
    a = a * vig[..., None] + rng.normal(0, .025, a.shape)
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def stage(bg, *items):
    base = bg.convert('RGBA').resize((640, 640)) if isinstance(bg, Image.Image) else Image.new('RGBA', (640, 640), bg)
    for it, box in items:
        it = it.resize((box[2], box[3]), Image.LANCZOS)
        sh = Image.new('RGBA', it.size, (0, 0, 0, 0)); sh.putalpha(it.split()[3].point(lambda p: int(p * .55)))
        base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), (box[0] + 14, box[1] + 18))
        base.alpha_composite(it, (box[0], box[1]))
    return base


def glowbg(c1, c2, spots=()):
    g = Image.new('RGBA', (640, 640), c2)
    d = ImageDraw.Draw(g)
    d.ellipse([80, 40, 560, 520], fill=c1)
    g = g.filter(ImageFilter.GaussianBlur(120))
    d = ImageDraw.Draw(g)
    for (x, y, r, c) in spots:
        d.ellipse([x - r, y - r, x + r, y + r], fill=c)
    return g.filter(ImageFilter.GaussianBlur(3))


ball = Image.open(f'{D}/discoball.png').convert('RGBA')
bb = Image.open(f'{D}/boombox.png').convert('RGBA')
mic = Image.open(f'{D}/mic.png').convert('RGBA')
tree = Image.open(f'{D}/tree.png').convert('RGBA')
wood = Image.open(f'{D}/wood.jpg').convert('RGBA')
P = {}
spots = [(int(rng.integers(0, 640)), int(rng.integers(0, 640)), int(rng.integers(3, 9)), (255, 200, 240, 160)) for _ in range(30)]
P['ball'] = grade(stage(glowbg((120, 40, 160, 255), (14, 4, 30, 255), spots), (ball, (110, 90, 420, 420))))
wb = wood.crop((200, 400, 840, 1040)).filter(ImageFilter.GaussianBlur(2))
P['boombox'] = grade(stage(wb, (bb, (30, 150, 580, 378))), 1.05)
P['mic'] = grade(stage(glowbg((150, 30, 30, 255), (20, 4, 4, 255)), (mic, (250, 40, 160, 520))))
P['tree'] = grade(stage(glowbg((110, 50, 20, 255), (18, 6, 4, 255)), (tree, (120, 40, 420, 560))), 1.06)
crops = {'neon90': ('poster-ny-disco90.png', (.08, .52, .92, .78)), 'cassette': ('poster-ny-disco90.png', (0, .55, .3, .77)),
         'tv': ('poster-ny-disco90-retro.png', (.18, .33, .74, .7)), 'niche': ('poster-ny-disco90-advent.png', (.25, .16, .75, .67)),
         'gifts': ('poster-ny-disco90.png', (.0, .8, .62, 1.0)), 'stamp': ('poster-ny-disco90-retro.png', (0, .6, .28, .8))}
for k, (f, (x0, y0, x1, y1)) in crops.items():
    im = Image.open(f'{D}/{f}')
    w, h = im.size
    c = im.crop((int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h)))
    s = min(c.size); c = c.crop(((c.width - s) // 2, (c.height - s) // 2, (c.width - s) // 2 + s, (c.height - s) // 2 + s))
    P[k] = grade(c)
for k, im in P.items():
    im.save(f'{D}/board-{k}.jpg', quality=88)
print('photos ok', list(P))
