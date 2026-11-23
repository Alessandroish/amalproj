"""Draped white cloth (height field + lighting) for the gallery poster.
Usage: python3 make_cloth.py out.png   -> RGBA covering x 130..270 mm, y 108..362 mm at 8 px/mm"""
import sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
out = sys.argv[1]
S = 8
X0, Y0, X1, Y1 = 130, 108, 270, 362
W, H = (X1 - X0) * S, (Y1 - Y0) * S
rng = np.random.default_rng(5)
pts = [(188, 119), (210, 116), (232, 116), (247, 118), (255, 124), (258, 146), (261, 190), (263, 240), (263, 284), (259, 312), (262, 330), (259, 346),
       (240, 354), (210, 356), (180, 357), (156, 355), (140, 350), (138, 344), (150, 339), (172, 334), (196, 330), (212, 326),
       (216, 300), (210, 262), (214, 222), (209, 182), (211, 148), (206, 132), (196, 125)]
m = Image.new('L', (W, H), 0)
def cr(P, n=12):
    out = []
    for i in range(len(P)):
        p0, p1, p2, p3 = P[i - 1], P[i], P[(i + 1) % len(P)], P[(i + 2) % len(P)]
        for k in range(n):
            t = k / n
            out.append(tuple(.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in (0, 1)))
    return out
ImageDraw.Draw(m).polygon([((x - X0) * S, (y - Y0) * S) for x, y in cr(pts)], fill=255)
mask = np.asarray(m.filter(ImageFilter.GaussianBlur(1.2))).astype(np.float64) / 255
yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
x = xx / S + X0; y = yy / S + Y0
# right edge of the hanging part as a function of y
xr = np.interp(y, [118, 146, 190, 240, 284, 312, 326], [250, 258, 261, 263, 263, 259, 260])
u = np.clip((x - 211) / (xr - 211), -.2, 1.2)
t = np.clip((y - 128) / 200, 0, 1)
hang = (.9 * np.cos(2 * math.pi * (u * 2.2 + .25 * np.sin(t * 3.1) + .1)) * (.4 + .6 * t)
        + .45 * np.cos(2 * math.pi * (u * 4.3 + .4 * t + .3)) * (.3 + .7 * t)
        + .25 * np.cos(2 * math.pi * (u * 7.1 - .6 * t)) * t)
pool_v = (y - 326) / 28
pool = (.8 * np.cos(2 * math.pi * (pool_v * 1.6 + (x - 140) * .006)) + .4 * np.cos(2 * math.pi * (pool_v * 3.2 - (x - 140) * .012 + .2))
        + .35 * np.cos(2 * math.pi * ((x - 140) / 34 + pool_v * .5)))
topf = .7 * np.cos(2 * math.pi * ((y - 116) / 9 + (x - 188) * .015)) + .4 * np.cos(2 * math.pi * (x - 188) / 22)
wb = np.clip((y - 318) / 14, 0, 1); wb = wb * wb * (3 - 2 * wb)
wt = np.clip((130 - y) / 8, 0, 1); wt = wt * wt * (3 - 2 * wt)
h = hang * (1 - wb) * (1 - wt) + pool * wb + topf * wt
# edges roll under
h = h * (.35 + .65 * np.clip(mask * 1.3, 0, 1))
gy, gx = np.gradient(h * 26)
nx, ny, nz = -gx, -gy, np.ones_like(h)
ln = np.sqrt(nx * nx + ny * ny + nz * nz)
L = np.array([-.45, -.6, .66]); L /= np.linalg.norm(L)
lam = np.clip((nx * L[0] + ny * L[1] + nz * L[2]) / ln, 0, 1)
v = .52 + .55 * lam
v = v * (1 - .18 * np.clip(1 - mask * 1.15, 0, 1))
base = np.array([.985, .965, .925])
col = np.clip(base[None, None, :] * v[..., None] + np.array([.0, .0, .02]) * (1 - v[..., None]), 0, 1)
rgba = np.dstack([col, mask])
Image.fromarray((rgba * 255).astype(np.uint8), 'RGBA').save(out, optimize=True)
print('cloth ok', W, H)
