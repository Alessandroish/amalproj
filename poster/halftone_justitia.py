# Bitmap-halftone bust of Justitia for poster-law-halftone.html.
# Source: File:Statue_Justitia.jpg (Breandan Fischer, CC BY-SA 4.0), the 3840px thumbnail:
#   upload.wikimedia.org/wikipedia/commons/thumb/<h0>/<h0h1>/Statue_Justitia.jpg/3840px-Statue_Justitia.jpg
# Usage: python3 halftone_justitia.py justitia-3840.jpg
import sys
from PIL import Image, ImageFilter, ImageDraw
import numpy as np

im = Image.open(sys.argv[1] if len(sys.argv) > 1 else 'justitia-3840.jpg').convert('RGB')
k = im.width / 480                                   # coordinates below are on a 480px preview
box = tuple(int(v*k) for v in (158, 112, 352, 340))  # head + shoulders + chest
im = im.crop(box)

# --- cut out: cream stone vs saturated green grass
a = np.asarray(im).astype(float); r, g, b = a[...,0], a[...,1], a[...,2]
mx = a.max(-1); mn = a.min(-1); sat = (mx - mn) / (mx + 1)
m = (g - (r + b)/2 < 30) & (mx > 20)    # "greenness": stone -10..14, grass 50+
mask = Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.MedianFilter(9))
mask = mask.filter(ImageFilter.MaxFilter(11)).filter(ImageFilter.MinFilter(11))  # close small gaps
mask = mask.filter(ImageFilter.MinFilter(9)).filter(ImageFilter.MaxFilter(9))    # drop specks
# keep only the statue: flood from a point on the chest
mk = mask.point(lambda v: 255 if v > 127 else 0)
ImageDraw.floodfill(mk, (mk.width//2, int(mk.height*.55)), 128)
mask = mk.point(lambda v: 255 if v == 128 else 0)
pad = Image.new('L', (mask.width+2, mask.height+2), 0); pad.paste(mask, (1, 1))
ImageDraw.floodfill(pad, (0, 0), 128)
P = np.asarray(pad)[1:-1, 1:-1]
# the bottom edge is cut by the crop; keep everything that is not outside background
keep = (P != 128)
mask = Image.fromarray((keep*255).astype(np.uint8)).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(2))
A = np.asarray(mask).astype(float) / 255

S = 2
im = im.resize((im.width*S, im.height*S), Image.LANCZOS)
A = np.asarray(Image.fromarray((A*255).astype(np.uint8)).resize(im.size, Image.LANCZOS)).astype(float)/255
L = np.asarray(im.convert('L')).astype(float) / 255

def blur(x, rad):
    return np.asarray(Image.fromarray((np.clip(x,0,1)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(rad))).astype(float)/255

# --- tone: bright marble, punchy shadows in folds, blindfold and face
T = blur(L, 2)
T = T + 0.9*(T - blur(L, 14)) + 0.7*(T - blur(L, 70))
lo, hi = np.percentile(T[A > .5], [3, 88])
T = np.clip((T - lo) / (hi - lo), 0, 1) ** .8
H, W = T.shape; yy, xx = np.mgrid[0:H, 0:W]
T = T * np.clip(1.1 - np.clip((yy/H - .4)/.45, 0, 1)**.9*1.0, 0, 1)      # sink into dark at the bottom
dark = np.clip(1 - T, 0, 1) ** 1.35

# --- 45-degree dot screen
c = 15.0
u = (xx + yy) / np.sqrt(2); v = (xx - yy) / np.sqrt(2)
du = (u % c) - c/2; dv = (v % c) - c/2
d = np.sqrt(du*du + dv*dv)
rad = c * 0.74 * np.sqrt(dark)
ink = np.clip(rad - d + 0.5, 0, 1)

paper = np.array([238, 234, 226.]); inkc = np.array([18, 16, 16.])
rgb = paper*(1 - ink[..., None]) + inkc*ink[..., None]
out = Image.fromarray(rgb.astype(np.uint8))
out.putalpha(Image.fromarray((A*255).astype(np.uint8)))
out.save('statue-justitia-halftone.png', optimize=True)
print(out.size)
