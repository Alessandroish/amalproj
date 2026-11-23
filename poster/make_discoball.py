"""Mirror disco ball: flat square facets on a tilted sphere, each reflecting a colourful party environment.
Usage: python3 make_discoball.py out.png [size]"""
import sys
import numpy as np
from PIL import Image

out = sys.argv[1]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 1800
rng = np.random.default_rng(90)
R = N / 2 - 2
yy, xx = np.mgrid[0:N, 0:N].astype(np.float64)
x = (xx - N / 2 + .5) / R
y = -(yy - N / 2 + .5) / R
r2 = x * x + y * y
inside = r2 <= 1
z = np.sqrt(np.clip(1 - r2, 0, 1))

# tilt the sphere so the facet rows curve nicely
def rot(ax, ay, az, a, b):
    ca, sa, cb, sb = np.cos(a), np.sin(a), np.cos(b), np.sin(b)
    y1 = ay * ca - az * sa; z1 = ay * sa + az * ca
    x2 = ax * cb + z1 * sb; z2 = -ax * sb + z1 * cb
    return x2, y1, z2

px, py, pz = rot(x, y, z, .38, -.22)
lat = np.arcsin(np.clip(py, -1, 1))
lon = np.arctan2(px, pz)
rows = 30
dt = np.pi / rows
i = np.floor((lat + np.pi / 2) / dt)
latc = -np.pi / 2 + (i + .5) * dt
ncol = np.maximum(4, np.round(2 * np.pi * np.cos(latc) / dt))
dl = 2 * np.pi / ncol
j = np.floor((lon + np.pi) / dl)
lonc = -np.pi + (j + .5) * dl
fi = (lat + np.pi / 2) / dt - i
fj = (lon + np.pi) / dl - j
grout = (fi < .05) | (fi > .95) | (fj < .05) | (fj > .95)

# facet centre normal (in sphere space) -> back to view space
cx = np.cos(latc) * np.sin(lonc); cy = np.sin(latc); cz = np.cos(latc) * np.cos(lonc)
def unrot(ax, ay, az, a, b):
    cb, sb = np.cos(-b), np.sin(-b)
    x1 = ax * cb + az * sb; z1 = -ax * sb + az * cb
    ca, sa = np.cos(-a), np.sin(-a)
    y2 = ay * ca - z1 * sa; z2 = ay * sa + z1 * ca
    return x1, y2, z2
nx, ny, nz = unrot(cx, cy, cz, .38, -.22)
# per-facet random tilt (mirror tiles are never perfectly aligned)
tid = (i * 1000 + j).astype(np.int64)
uniq, inv = np.unique(np.where(inside, tid, -1), return_inverse=True)
jit = rng.normal(0, .085, (len(uniq), 3)); bri = rng.uniform(.5, 1.15, len(uniq)); spark = rng.random(len(uniq))
inv = inv.reshape(tid.shape)
nx = nx + jit[inv, 0]; ny = ny + jit[inv, 1]; nz = nz + jit[inv, 2]
nl = np.sqrt(nx * nx + ny * ny + nz * nz); nx /= nl; ny /= nl; nz /= nl
# reflect view (0,0,1)
d = nz
rx, ry, rz = 2 * d * nx, 2 * d * ny, 2 * d * nz - 1

def lamp(lx, ly, lz, col, k, amp):
    L = np.array([lx, ly, lz]); L = L / np.linalg.norm(L)
    c = rx * L[0] + ry * L[1] + rz * L[2]
    w = np.exp(-(1 - c) * k) * amp
    return w[..., None] * np.array(col)[None, None, :]

# environment: dark room, magenta floor glow, cyan & pink & gold spots, white key light
base = np.zeros((N, N, 3))
up = np.clip(ry, -1, 1)[..., None]
base += np.where(up > 0, (1 - up) * np.array([.16, .10, .32]) + up * np.array([.05, .04, .14]),
                 (1 + up) * np.array([.16, .10, .32]) + (-up) * np.array([.55, .12, .42]))
env = base + .1 + .5 * np.exp(-(1 - rz) * 3)[..., None] * np.array([.55, .55, .62])
env = env + lamp(-.7, .45, .55, [1.0, .25, .75], 7, 1.6)
env = env + lamp(.75, .25, .6, [.2, .85, 1.0], 7, 1.5)
env = env + lamp(.15, .85, .5, [1.0, .82, .45], 10, 1.4)
env = env + lamp(.45, .55, .7, [1, 1, 1], 26, 3.2)
env = env + lamp(-.3, -.6, .7, [.6, .3, 1.0], 6, .9)
col = env * bri[inv][..., None]
# a few facets catch the light hard
hot = (spark[inv] > .955)[..., None]
col = np.where(hot, np.clip(col * 2.2 + .35, 0, 1.6), col)
# slight gradient across each facet (flat mirror, but light falls off)
col *= (1.08 - .16 * fi[..., None]) * (1 + .05 * rng.standard_normal((N, N)))[..., None] ** 0 * 1
# rim darkening and grout
rim = np.clip(z, 0, 1) ** .35
col *= rim[..., None]
col = np.where(grout[..., None], col * .18 + .02, col)
img = np.clip(col, 0, 1)
img = (img ** (1 / 1.1) * 255).astype(np.uint8)
# soft antialiased edge
edge = np.clip((1 - np.sqrt(r2)) * R / 1.5, 0, 1)
alpha = (edge * 255).astype(np.uint8)
rgba = np.dstack([img, alpha])
Image.fromarray(rgba, 'RGBA').save(out, optimize=True)
print(out, rgba.shape)
