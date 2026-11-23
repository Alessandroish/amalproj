"""Photoreal-ish props for the advent poster, rendered with numpy shading (light from the top-left).
Usage: python3 make_props.py <outdir>  ->  boombox.png, mic.png"""
import sys, math
import numpy as np
from PIL import Image, ImageFilter

out = sys.argv[1]
rng = np.random.default_rng(7)
LX, LY, LZ = -.45, -.55, .7
_l = math.sqrt(LX * LX + LY * LY + LZ * LZ); LX, LY, LZ = LX / _l, LY / _l, LZ / _l


def rrect_sdf(xx, yy, x0, y0, x1, y1, r):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hx, hy = (x1 - x0) / 2 - r, (y1 - y0) / 2 - r
    qx, qy = np.abs(xx - cx) - hx, np.abs(yy - cy) - hy
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r


def cov(sdf, aa=1.0):
    return np.clip(.5 - sdf / aa, 0, 1)


def bevel_shade(sdf, width, strength=1.0):
    """height rises over `width` from the edge; returns lambert factor of the bevel"""
    h = np.clip(-sdf / width, 0, 1)
    h = np.sin(h * np.pi / 2)
    gy, gx = np.gradient(h)
    nx, ny, nz = -gx * width * strength, -gy * width * strength, np.ones_like(h)
    n = np.sqrt(nx * nx + ny * ny + nz * nz)
    return (nx * LX + ny * LY + nz * LZ) / n / LZ


class Canvas:
    def __init__(s, W, H):
        s.W, s.H = W, H
        s.rgb = np.zeros((H, W, 3)); s.a = np.zeros((H, W))
        s.yy, s.xx = np.mgrid[0:H, 0:W].astype(np.float64)

    def over(s, col, alpha):
        alpha = np.clip(alpha, 0, 1)[..., None]
        col = np.broadcast_to(np.asarray(col, np.float64), s.rgb.shape) if np.ndim(col) == 1 else col
        s.rgb = s.rgb * (1 - alpha) + col * alpha
        s.a = s.a + (1 - s.a) * alpha[..., 0]

    def save(s, path, blur_shadow=None):
        img = np.dstack([np.clip(s.rgb, 0, 1), np.clip(s.a, 0, 1)])
        Image.fromarray((img * 255).astype(np.uint8), 'RGBA').save(path, optimize=True)


def brushed(H, W, scale=.05, rx=120):
    n = rng.standard_normal((H, W))
    c = np.cumsum(np.pad(n, ((0, 0), (rx + 1, rx)), mode='wrap'), axis=1)
    n = (c[:, 2 * rx + 1:] - c[:, :-2 * rx - 1]) / (2 * rx + 1)
    return n / n.std() * scale


# ======================= BOOMBOX =======================
S = 20  # px per mm
W, H = 92 * S, 60 * S
c = Canvas(W, H)
xx, yy = c.xx / S, c.yy / S  # mm coords
ox, oy = 4, 14               # body origin (mm)
bw, bh = 84, 40
# handle (chrome tube): drawn first, behind body top
for i, (w, col) in enumerate([(3.4, (.12, .12, .13)), (3.0, (.45, .46, .5)), (2.2, (.75, .76, .8)), (1.1, (.95, .95, .97)), (.45, (1, 1, 1))]):
    t = np.linspace(0, 1, 400)
    px = ox + 20 + 44 * t
    py = oy + 1 - 11 * np.sin(np.pi * t) ** .6 - (.5 if i > 2 else 0) - (.35 if i == 4 else 0)
    d = np.full((H, W), 1e9)
    for k in range(0, 400, 2):
        d = np.minimum(d, np.hypot(xx - px[k], yy - py[k]))
    c.over(col, cov((d - w / 2) * S))
# handle posts
for hx in (ox + 18.5, ox + 63.5):
    sd = rrect_sdf(xx, yy, hx, oy - 2.5, hx + 4, oy + 1, .8)
    c.over((.18, .18, .2), cov(sd * S))
    c.over((.55, .56, .6), cov(sd * S) * np.clip(1 - (xx - hx) / 2, 0, 1) * .6)
# antenna
t = np.linspace(0, 1, 300)
ax0, ay0, ax1, ay1 = ox + 78, oy + 1, ox + 90, oy - 13
d = np.full((H, W), 1e9)
for k in range(300):
    d = np.minimum(d, np.hypot(xx - (ax0 + (ax1 - ax0) * t[k]), yy - (ay0 + (ay1 - ay0) * t[k])))
c.over((.35, .35, .38), cov((d - .55) * S)); c.over((.9, .9, .93), cov((d - .22) * S) * .8)
# body
sdf = rrect_sdf(xx, yy, ox, oy, ox + bw, oy + bh, 4.5)
shade = bevel_shade(sdf * S, 1.6 * S)
grad = .92 - .22 * (yy - oy) / bh
base = np.array([.66, .67, .7])
body = base[None, None, :] * (grad * shade)[..., None] + brushed(H, W, .03)[..., None]
c.over(body, cov(sdf * S))
# darker lower panel
sd2 = rrect_sdf(xx, yy, ox + 1.4, oy + 9, ox + bw - 1.4, oy + bh - 1.4, 3.4)
lower = np.array([.2, .2, .22])[None, None, :] * (bevel_shade(-sd2 * S - 0, .8 * S) * (1 - .25 * (yy - oy) / bh))[..., None]
c.over(lower, cov(sd2 * S))
# speakers: chrome ring + perforated grille + cone hint
for scx in (ox + 15.5, ox + bw - 15.5):
    scy = oy + 25
    r = np.hypot(xx - scx, yy - scy)
    ring = (r < 13.2) & (r > 11.6)
    ang = np.arctan2(yy - scy, xx - scx)
    chrome = .55 + .45 * np.cos(ang + 2.3) ** 3 * np.sign(np.cos(ang + 2.3))
    c.over(np.dstack([chrome * .95, chrome * .96, chrome]), cov((r - 13.2) * S) * cov((11.4 - r) * S))
    # grille: dark metal with hex holes, domed shading
    g = r < 11.4
    z = np.sqrt(np.clip(1 - (r / 11.6) ** 2, 0, 1))
    nx, ny = (xx - scx) / 11.6, (yy - scy) / 11.6
    lam = np.clip((nx * LX + ny * LY) * .35 + z * LZ, 0, 1.4)
    hx = (xx - scx) / .9; hy = (yy - scy) / .78
    holes = ((np.sin(hx * np.pi) * np.sin(hy * np.pi + (np.floor(hx) % 2) * np.pi / 2)) > .35)
    grille = np.array([.12, .12, .13])[None, None, :] * (.6 + .8 * lam)[..., None]
    grille = np.where(holes[..., None], grille * .25, grille + .06 * lam[..., None])
    c.over(grille, cov((r - 11.4) * S))
    # specular arc
    c.over((1, 1, 1), np.exp(-((r - 10.5) ** 2) / .25) * np.clip(np.cos(ang + 2.2), 0, 1) ** 4 * .5)
    # brand dot
    c.over((.85, .2, .25), cov((np.hypot(xx - scx, yy - scy - 9.2) - .6) * S))
# cassette deck
dsd = rrect_sdf(xx, yy, ox + 31.5, oy + 13, ox + bw - 31.5, oy + 37, 1.2)
c.over(np.array([.06, .06, .07])[None, None, :] * np.ones((H, W, 1)), cov(dsd * S))
c.over(np.array([.25, .25, .28])[None, None, :] * np.ones((H, W, 1)), cov(np.abs(dsd + .2) * S - 2) * .8)
wsd = rrect_sdf(xx, yy, ox + 33, oy + 15, ox + bw - 33, oy + 27, 1)
win = np.dstack([.14 + 0 * xx, .1 + 0 * xx, .16 + 0 * xx])
c.over(win, cov(wsd * S))
# label + reels inside the window
lsd = rrect_sdf(xx, yy, ox + 34.5, oy + 16, ox + bw - 34.5, oy + 26, .5)
c.over((.86, .82, .72), cov(lsd * S) * .9)
c.over((.85, .15, .35), cov(rrect_sdf(xx, yy, ox + 34.5, oy + 16, ox + bw - 34.5, oy + 17.6, .3) * S))
for rx_ in (ox + 38.5, ox + bw - 38.5):
    rr = np.hypot(xx - rx_, yy - (oy + 21.5))
    c.over((.12, .1, .1), cov((rr - 2.6) * S))
    c.over((.92, .92, .94), cov((rr - 1.7) * S))
    c.over((.15, .15, .16), cov((rr - .9) * S))
c.over((.28, .2, .14), cov(rrect_sdf(xx, yy, ox + 41.5, oy + 19.5, ox + bw - 41.5, oy + 23.5, .3) * S) * .9)
# window glass reflection
refl = np.clip(1 - np.abs((xx - ox - 33) - (yy - oy - 15) * 1.6 - 3) / 2.2, 0, 1) * .35 + np.clip(1 - np.abs((xx - ox - 33) - (yy - oy - 15) * 1.6 - 8) / .8, 0, 1) * .2
c.over((1, 1, 1), refl * cov(wsd * S))
# piano keys
for k in range(5):
    kx = ox + 33 + k * 3.7
    ksd = rrect_sdf(xx, yy, kx, oy + 29, kx + 3.2, oy + 34, .4)
    kshade = (1.05 - .45 * (yy - oy - 29) / 5) * bevel_shade(ksd * S, .5 * S)
    col = np.array([.78, .79, .82]) if k != 2 else np.array([.85, .2, .22])
    c.over(col[None, None, :] * kshade[..., None], cov(ksd * S))
# VU / tuner strip on the top band
tsd = rrect_sdf(xx, yy, ox + 28, oy + 3, ox + bw - 28, oy + 7, .6)
c.over((.05, .06, .05), cov(tsd * S))
for k in range(14):
    lx_ = ox + 29.5 + k * 1.9
    on = k < 9
    col = (.2, .95, .4) if k < 7 else (1, .8, .2) if k < 10 else (1, .25, .2)
    c.over(col if on else (.15, .2, .15), cov(rrect_sdf(xx, yy, lx_, oy + 4, lx_ + 1.2, oy + 6, .2) * S) * (1 if on else .6))
for kx in (ox + 7, ox + 12, ox + bw - 12, ox + bw - 7):    # knobs on the top band
    rr = np.hypot(xx - kx, yy - (oy + 5))
    ang = np.arctan2(yy - oy - 5, xx - kx)
    knob = .45 + .35 * np.cos(ang + 2.4) + .1 * np.sin(ang * 24)
    c.over(np.dstack([knob, knob, knob * 1.02]), cov((rr - 1.9) * S))
c.over((.2, .2, .22), cov(rrect_sdf(xx, yy, ox + 2, oy + 8.6, ox + bw - 2, oy + 9.2, .2) * S) * .8)
# label text-like logo
c.over((.15, .15, .17), cov(rrect_sdf(xx, yy, ox + 39, oy + 38.2, ox + bw - 39, oy + 39, .2) * S) * .7)
# feet
for fx in (ox + 6, ox + bw - 14):
    c.over((.05, .05, .05), cov(rrect_sdf(xx, yy, fx, oy + bh - .5, fx + 8, oy + bh + 1.4, .5) * S))
# warm rim light from the tree on the right side + overall subtle warm tint
c.rgb = c.rgb * np.array([1.04, 1.0, .95])
c.save(f'{out}/boombox.png')
print('boombox ok')

# ======================= MICROPHONE ON A STAND =======================
S = 20
W, H = 34 * S, 110 * S
c = Canvas(W, H)
xx, yy = c.xx / S, c.yy / S
cx = 17
# base disc (ellipse) + rod
ex, ey, erx, ery = cx, 104, 13, 3.2
ed = np.hypot((xx - ex) / erx, (yy - ey) / ery) - 1
side = (np.abs(xx - ex) < erx) & (yy > ey) & (yy < ey + 1.6)
rimd = np.hypot((xx - ex) / erx, (yy - ey - 1.6) / ery) - 1
c.over((.05, .05, .06), cov(np.minimum(rimd, np.where(side, -1, 1)) * S * 3))
top = np.clip(1 - ((xx - ex + 4) / erx) ** 2 - ((yy - ey + 1) / ery) ** 2, 0, 1)
c.over(np.dstack([.15 + .7 * top ** 2, .15 + .7 * top ** 2, .17 + .72 * top ** 2]), cov(ed * S * 3))
def cyl(x0, x1, y0, y1, colmul, spec=.8, dark=.25):
    t = (xx - x0) / (x1 - x0)
    inside = (xx >= x0) & (xx <= x1) & (yy >= y0) & (yy <= y1)
    lam = np.clip(np.cos((t - .32) * np.pi * .95), 0, 1)
    v = dark + (1 - dark) * lam + spec * np.exp(-((t - .28) ** 2) / .004)
    a = cov(np.maximum(np.maximum(x0 - xx, xx - x1), np.maximum(y0 - yy, yy - y1)) * S)
    c.over(np.dstack([v * colmul[0], v * colmul[1], v * colmul[2]]), a)
cyl(cx - .9, cx + .9, 46, 104, (.85, .86, .9))
cyl(cx - 1.6, cx + 1.6, 44, 47.5, (.2, .2, .22), .3)   # clutch
cyl(cx - 1.2, cx + 1.2, 38, 44, (.75, .76, .8))
# clip holder (black)
cyl(cx - 3.2, cx + 3.2, 30, 38, (.12, .12, .13), .35, .35)
# handle: tapered black cylinder
yb0, yb1 = 13, 44
for k in range(int((yb1 - yb0) * S)):
    pass
t = (yy - yb0) / (yb1 - yb0)
hw = 3.4 - 1.4 * np.clip(t, 0, 1)
u = (xx - cx) / hw
inside = (np.abs(u) <= 1) & (yy >= yb0) & (yy <= yb1)
lam = np.clip(np.cos((u * .5 + .5 - .32) * np.pi * .95), 0, 1)
v = .05 + .22 * lam + .35 * np.exp(-((u + .45) ** 2) / .01)
c.over(np.dstack([v, v, v * 1.05]), cov(np.maximum(np.abs(u) - 1, np.maximum(yb0 - yy, yy - yb1) / 3) * S * hw))
# collar
cyl(cx - 3.9, cx + 3.9, 11.2, 13.4, (.8, .81, .85))
# grille ball
gcx, gcy, gr = cx, 5.6, 6.4
r = np.hypot(xx - gcx, yy - gcy) / gr
z = np.sqrt(np.clip(1 - r * r, 0, 1))
nx, ny = (xx - gcx) / gr, (yy - gcy) / gr
lam = np.clip(nx * LX + ny * LY + z * LZ, 0, 1)
sx, sy = (xx - gcx) / (z * .6 + .4), (yy - gcy) / (z * .6 + .4)
mesh = (np.abs(np.sin((sx + sy) * 6.5)) < .32) | (np.abs(np.sin((sx - sy) * 6.5)) < .32)
v = .22 + .7 * lam
col = np.dstack([v, v, v * 1.03])
col = np.where(mesh[..., None], col * 1.08 + .05, col * .35)
spec = np.exp(-((nx + .4) ** 2 + (ny + .45) ** 2) / .03) * .9
col = col + spec[..., None]
c.over(col, cov((r - 1) * gr * S))
# warm rim from the tree (right side)
rim = np.exp(-((r - .93) ** 2) / .004) * np.clip(nx, 0, 1)
c.over((1, .75, .45), rim * .6 * (r < 1.02))
c.save(f'{out}/mic.png')
print('mic ok')
