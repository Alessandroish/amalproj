"""Crumpled-paper shading map (grey, 1.0 = flat paper) computed in float, so no 8-bit terracing.
Usage: python3 make_crumple.py out.png [width height seed]
Folds: band-limited noise; creases: ridged noise (1-|n|)^p at several scales; Lambert light from the top-right."""
import sys
import numpy as np
from PIL import Image

out = sys.argv[1]
W = int(sys.argv[2]) if len(sys.argv) > 2 else 2568
H = int(sys.argv[3]) if len(sys.argv) > 3 else 3144
seed = int(sys.argv[4]) if len(sys.argv) > 4 else 7
rng = np.random.default_rng(seed)
fy = np.fft.fftfreq(H)[:, None]
fx = np.fft.fftfreq(W)[None, :]
fr = np.sqrt(fx * fx + fy * fy)


def band(period_px, width=.55):
    """random field with energy around one spatial period, unit variance"""
    f0 = 1 / period_px
    spec = np.exp(-((np.log(fr + 1e-9) - np.log(f0)) ** 2) / (2 * width ** 2))
    n = np.fft.fft2(rng.standard_normal((H, W)))
    f = np.real(np.fft.ifft2(n * spec))
    return f / f.std()


h = np.zeros((H, W))
# soft folds
h += .5 * band(1100) + .25 * band(520)
# creases: straight ridges/valleys (tent profile) of random length and angle -> facets like real crumpled paper
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
for i in range(140):
    cx, cy = rng.uniform(-.1, 1.1) * W, rng.uniform(-.1, 1.1) * H
    ang = rng.uniform(0, np.pi)
    if rng.random() < .55:  # dominant diagonal direction, as when a sheet is squeezed
        ang = rng.normal(2.4, .35)
    c, s_ = np.cos(ang), np.sin(ang)
    length = rng.uniform(.25, 1.0) * W
    w = rng.uniform(16, 80)
    amp = rng.choice([-1, 1]) * rng.uniform(.5, 1.5) * (w / 70)
    d = (xx - cx) * -s_ + (yy - cy) * c          # across the crease
    t = (xx - cx) * c + (yy - cy) * s_           # along the crease
    prof = np.clip(1 - np.abs(d) / w, 0, None)
    ends = np.clip(1 - (np.abs(t) / (length / 2)) ** 2, 0, None)
    h += amp * prof * ends
# fine crinkle + paper tooth
h += .06 * (1 - np.abs(np.tanh(band(70, .4)))) ** 2
h += .03 * band(6, .8)

gy, gx = np.gradient(h)
k = 7.0
nx, ny, nz = -gx * k, -gy * k, np.ones_like(h)
ln = np.sqrt(nx * nx + ny * ny + nz * nz)
L = np.array([.42, -.5, .76]); L /= np.linalg.norm(L)  # light from the top-right
lam = (nx * L[0] + ny * L[1] + nz * L[2]) / ln
flat = L[2]
shade = lam / flat
shade = np.clip(shade, .5, 1.12)
# neutral grey 128 = flat paper; meant for mix-blend-mode: hard-light
img = np.clip(shade * 128, 0, 255).astype(np.uint8)
Image.fromarray(img, 'L').save(out, optimize=True)
print(out, img.shape, float(shade.mean()), float(shade.min()))
