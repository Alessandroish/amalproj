# Full-length halftone figure of Augustus of Prima Porta (raised arm = adlocutio, the orator's gesture)
# for poster-networking-shadows.html.
# Source: File:Statue-Augustus.jpg (Till Niermann, Wikimedia Commons, public domain), 1500x2250:
#   upload.wikimedia.org/wikipedia/commons/<md5[0]>/<md5[:2]>/Statue-Augustus.jpg
# Cut-out by colour (marble is warm, the backdrop is cold blue-grey), as in relight_augustus.py; cupid and pedestal dropped.
# Usage: python3 halftone_augustus.py aug.jpg [figure-augustus.png]
import sys
from PIL import Image, ImageFilter, ImageDraw
import numpy as np

im = Image.open(sys.argv[1] if len(sys.argv) > 1 else 'aug.jpg').convert('RGB')
out_path = sys.argv[2] if len(sys.argv) > 2 else 'figure-augustus.png'
a = np.asarray(im).astype(float); r, g, b = a[...,0], a[...,1], a[...,2]
m = (r - b > 10) | ((r+g+b)/3 > 200)
m[2125:] = False                      # pedestal
# cupid and dolphin at the left leg: drop everything left of the leg's contour (traced on the original)
cup = Image.new('L', im.size, 0)
ImageDraw.Draw(cup).polygon([(0,1440),(756,1440),(762,1500),(768,1600),(770,1700),(780,1800),(793,1900),(812,1975),
                             (832,2010),(818,2048),(792,2075),(772,2100),(764,2125),(0,2125)], fill=255)
m &= np.asarray(cup) == 0
mask = Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.MedianFilter(5))
mask = mask.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9))
pad = Image.new('L', (mask.width+2, mask.height+2), 0); pad.paste(mask, (1, 1))
ImageDraw.floodfill(pad, (0, 0), 128)
mask = Image.fromarray(((np.asarray(pad)[1:-1, 1:-1] != 128)*255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
bb = mask.point(lambda v: 255 if v > 128 else 0).getbbox()
box = (bb[0]-6, bb[1]-6, bb[2]+6, bb[3]+2)
im = im.crop(box); mask = mask.crop(box)

S = 2
im = im.resize((im.width*S, im.height*S), Image.LANCZOS)
A = np.asarray(mask.resize(im.size, Image.LANCZOS)).astype(float) / 255
L = np.asarray(im.convert('L')).astype(float) / 255
L = L*A + .6*(1 - A)
def blur(x, rad):
    return np.asarray(Image.fromarray((np.clip(x,0,1)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(rad))).astype(float)/255
T = blur(L, 1.5)
T = T + .8*(T - blur(L, 10)) + .5*(T - blur(L, 50))
lo, hi = np.percentile(T[A > .5], [2, 97])
T = np.clip((T - lo)/(hi - lo), 0, 1)
H, W = T.shape; yy, xx = np.mgrid[0:H, 0:W]
T = T ** 1.35 * np.clip(1.15 - yy/H*.55, 0, 1)        # darker figure (as the dark figure of the reference), legs into shade
dark = np.clip(1 - T, 0, 1) ** 1.2

c = 11.0                                              # 45-degree dot screen
u = (xx + yy)/np.sqrt(2); v = (xx - yy)/np.sqrt(2)
du = (u % c) - c/2; dv = (v % c) - c/2
ink = np.clip(c*.74*np.sqrt(dark) - np.sqrt(du*du + dv*dv) + .5, 0, 1)
paper = np.array([240, 228, 200.]); inkc = np.array([20, 15, 15.])
rgb = paper*(1 - ink[..., None]) + inkc*ink[..., None]
out = Image.fromarray(rgb.astype(np.uint8)); out.putalpha(Image.fromarray((A*255).astype(np.uint8)))
out.save(out_path, optimize=True); print(out.size)
# hand tip (raised index finger) in normalized figure coordinates, for the shadow geometry in the HTML
ys, xs = np.nonzero(A > .5); i = np.argmin(xs + ys*.6)
print('hand tip', round(xs[i]/W, 4), round(ys[i]/H, 4))
