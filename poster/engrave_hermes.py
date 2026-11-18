# Banknote-style line engraving of the face of Hermes Ingenui for poster-networking-engraving.html.
# Source: File:Hermes_Ingenui_Pio-Clementino_Inv544.jpg (Marie-Lan Nguyen, 2009, public domain), 1600x3500.
# Close crop: hat brim, curls, eyes, nose (the "eyes through the torn paper" of the reference).
# Lines follow the form (phase displaced by blurred luminance); crosshatching in the deep shadows.
# Usage: python3 engrave_hermes.py hermes.jpg [engraving-hermes.png]
import sys
from PIL import Image, ImageFilter
import numpy as np
im = Image.open(sys.argv[1] if len(sys.argv) > 1 else 'hermes.jpg').convert('L')
out_path = sys.argv[2] if len(sys.argv) > 2 else 'engraving-hermes.png'
K = im.width / 900
box = tuple(int(v*K) for v in (318, 112, 682, 300))     # on the 900px preview: brim, curls, eyes, nose
im = im.crop(box)
S = 5
im = im.resize((im.width*S, im.height*S), Image.LANCZOS)
L = np.asarray(im).astype(float)/255
def blur(x, r): return np.asarray(Image.fromarray((np.clip(x,0,1)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(float)/255
T = blur(L, 2.5)
T = T + .9*(T - blur(L, 25)) + .4*(T - blur(L, 120))
lo, hi = np.percentile(T, [2, 98]); T = np.clip((T - lo)/(hi - lo), 0, 1) ** 1.1
dark = 1 - T
H, W = T.shape; yy, xx = np.mgrid[0:H, 0:W]
G = blur(L, 40)
p = 13.0
ph = yy + 70*G + 6*np.sin(xx/260.)                      # contour-following waves
d1 = np.abs((ph % p) - p/2)
ink = np.clip(p/2*np.clip(dark*1.05, 0, 1)**.85 - d1 + .9, 0, 1)
ph2 = (xx*.5 + yy*.87) + 40*G                           # crosshatch at 60 degrees in the shadows
d2 = np.abs((ph2 % 11) - 5.5)
ink2 = np.clip(5.5*np.clip((dark - .55)/.45, 0, 1) - d2 + .6, 0, 1) * np.clip((dark - .55)/.08, 0, 1)
ink = np.maximum(ink, ink2)
stip = (np.random.default_rng(3).random(T.shape) < .015*dark)   # a little stipple, as in banknote portraits
ink = np.maximum(ink, stip*.8)
paper = np.array([238, 226, 198.]); inkc = np.array([38, 28, 22.])
rgb = paper*(1 - ink[..., None]) + inkc*ink[..., None]
Image.fromarray(rgb.astype(np.uint8)).save(out_path, optimize=True); print(W, H)
