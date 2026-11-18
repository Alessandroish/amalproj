# Bitmap-halftone bust of Hermes for poster-networking-halftone.html.
# Source: File:Hermes_Ingenui_Pio-Clementino_Inv544.jpg (Vatican, Museo Pio-Clementino), public domain, 1600x3500:
#   upload.wikimedia.org/wikipedia/commons/<md5[0]>/<md5[:2]>/Hermes_Ingenui_Pio-Clementino_Inv544.jpg
# The niche wall is as bright as the marble, so the cut-out uses the hand-traced outline from relight_hermes.py.
# Crop: head, petasos, cloak and upper chest only (the statue is nude) - everything lower sinks into black.
# Usage: python3 halftone_hermes.py hermes.jpg [statue-hermes-halftone.png] [dots]
#   'dots' -> ink dots on transparency (for the red Gropius-style poster)
import sys
from PIL import Image, ImageFilter, ImageDraw
import numpy as np

im = Image.open(sys.argv[1] if len(sys.argv) > 1 else 'hermes.jpg').convert('RGB')
out_path = sys.argv[2] if len(sys.argv) > 2 else 'statue-hermes-halftone.png'
K = im.width / 900                                    # outline traced on a 900px-wide preview
outline = [(352,185),(360,130),(395,90),(440,68),(500,60),(560,68),(605,92),(630,125),(638,165),(628,205),
           (605,240),(575,258),(550,288),(534,320),(530,350),(542,372),(580,384),(615,405),(648,428),(668,420),
           (672,392),(678,365),(695,350),(718,352),(734,372),(730,398),(762,396),(800,393),(830,418),
           (845,458),(846,496),(826,497),(792,472),(768,468),(764,520),(754,560),(750,610),(762,660),
           (770,700),(782,760),(792,850),(796,930),
           (140,930),(178,880),(190,850),(184,790),(152,705),(138,640),(148,560),(172,470),(204,402),
           (240,362),(290,342),(320,332),(342,326),(380,328),(412,312),(420,272),(410,250),(388,240),(365,212)]
mask = Image.new('L', im.size, 0)
ImageDraw.Draw(mask).polygon([(x*K, y*K) for x, y in outline], fill=255)
L0 = np.asarray(im.convert('L')).astype(float)
M = np.asarray(mask).astype(float) / 255 * np.clip((L0 - 25) / 30, 0, 1)
mask = Image.fromarray((M*255).astype(np.uint8)).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(2))

box = tuple(int(v*K) for v in (120, 40, 870, 640))   # head + shoulders + upper chest
im = im.crop(box); mask = mask.crop(box)

S = 2
im = im.resize((im.width*S, im.height*S), Image.LANCZOS)
A = np.asarray(mask.resize(im.size, Image.LANCZOS)).astype(float) / 255
L = np.asarray(im.convert('L')).astype(float) / 255
L = L*A + 0.78*(1 - A)          # neutral fill outside, so local contrast does not draw a dark halo on the edge

def blur(x, rad):
    return np.asarray(Image.fromarray((np.clip(x,0,1)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(rad))).astype(float)/255

# --- tone: white marble -> bright, but deep shadows in curls, eyes and cloak folds
T = blur(L, 2)
T = T + 0.8*(T - blur(L, 14)) + 0.5*(T - blur(L, 70))
lo, hi = np.percentile(T[A > .5], [1, 97])
T = np.clip((T - lo) / (hi - lo), 0, 1) ** .75
H, W = T.shape; yy, xx = np.mgrid[0:H, 0:W]
T = T * np.clip(1.15 - np.clip((yy/H - .55)/.42, 0, 1)**.9*1.1, 0, 1)    # chest and below sink into dark
dark = np.clip(1 - T, 0, 1) ** 1.35

# --- 45-degree dot screen, 15px pitch (same as Justitia)
c = 15.0
u = (xx + yy) / np.sqrt(2); v = (xx - yy) / np.sqrt(2)
du = (u % c) - c/2; dv = (v % c) - c/2
d = np.sqrt(du*du + dv*dv)
ink = np.clip(c * 0.74 * np.sqrt(dark) - d + 0.5, 0, 1)

if len(sys.argv) > 3 and sys.argv[3] == 'dots':
    # dots only: ink on transparency, so the poster's red shows through the marble highlights
    rgb = np.zeros(ink.shape + (3,)) + np.array([22, 17, 17.])
    alpha = ink * np.clip(A*1.5, 0, 1) * np.clip((H - yy) / (0.16*H), 0, 1) ** 1.5   # no hard crop line at the bottom
else:
    paper = np.array([238, 234, 226.]); inkc = np.array([18, 16, 16.])
    rgb = paper*(1 - ink[..., None]) + inkc*ink[..., None]
    alpha = A
out = Image.fromarray(rgb.astype(np.uint8))
out.putalpha(Image.fromarray((alpha*255).astype(np.uint8)))
out.save(out_path, optimize=True)
print(out.size)
