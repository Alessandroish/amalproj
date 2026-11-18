# Hermes Ingenui (Vatican, Pio-Clementino), photo: Wikimedia Commons, public domain.
# Expects hermes.jpg (File:Hermes_Ingenui_Pio-Clementino_Inv544.jpg, 1600x3500) next to it.
# Waist-up crop, hand-traced outline (the niche wall is as bright as the marble), red relight as for Augustus.
import sys
from PIL import Image, ImageFilter, ImageDraw
import numpy as np

src = sys.argv[1] if len(sys.argv) > 1 else 'hermes.jpg'
out_path = sys.argv[2] if len(sys.argv) > 2 else 'statue-hermes.png'
im = Image.open(src).convert('RGB')
K = 1600 / 900  # outline traced on a 900px-wide preview

outline = [(352,185),(360,130),(395,90),(440,68),(500,60),(560,68),(605,92),(630,125),(638,165),(628,205),
           (605,240),(575,258),(550,288),(534,320),(530,350),(542,372),(580,384),(615,405),(648,428),(668,420),
           (672,392),(678,365),(695,350),(718,352),(734,372),(730,398),(762,396),(800,393),(830,418),
           (845,458),(846,496),(826,497),(792,472),(768,468),(764,520),(754,560),(750,610),(762,660),
           (770,700),(782,760),(792,850),(796,930),
           (140,930),(178,880),(190,850),(184,790),(152,705),(138,640),(148,560),(172,470),(204,402),
           (240,362),(290,342),(320,332),(342,326),(380,328),(412,312),(420,272),(410,250),(388,240),(365,212)]
hole = [(282,600),(298,582),(308,640),(316,740),(302,770),(282,752),(272,684)]

mask = Image.new('L', im.size, 0)
d = ImageDraw.Draw(mask)
d.polygon([(x*K, y*K) for x, y in outline], fill=255)
d.polygon([(x*K, y*K) for x, y in hole], fill=0)
# tighten to the marble where the statue is clearly brighter than its surroundings
L0 = np.asarray(im.convert('L')).astype(float)
M = np.asarray(mask).astype(float) / 255
M = M * np.clip((L0 - 70) / 40, 0, 1)
mask = Image.fromarray((M*255).astype(np.uint8)).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(2.2))

box = (0, 0, 1600, int(880*K))
mask = mask.crop(box); im = im.crop(box)
A = np.asarray(mask).astype(float) / 255
H, W = A.shape; yy, xx = np.mgrid[0:H, 0:W]
# fade the lower part out into shadow
A = A * np.clip((H - yy) / (0.26*H), 0, 1) ** 1.3
L = np.asarray(im.convert('L')).astype(float) / 255
def blur(x, r): return np.asarray(Image.fromarray((np.clip(x,0,1)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(float)/255
Ls = blur(L, 1.4)
D = Ls + 0.3*(Ls - blur(L, 4)) + 0.6*(Ls - blur(L, 30))
# white marble -> push mids down so the red ramp has depth; sun from upper-left
fall = np.clip(1.3 - 0.8*np.clip(xx/W*.6 + yy/H*.75 - .2, 0, 1.2), .15, 1.1)
D = np.clip((D - .30) / .62, 0, 1.2) * fall
edge = np.clip(A - blur(A, 8), 0, 1)
D = np.clip(D + edge*np.clip(1 - xx/W*1.4, 0, 1)*0.25, 0, 1) ** 1.25
stops = [(0,(8,1,1)),(.2,(48,5,4)),(.42,(125,18,11)),(.64,(205,55,30)),(.82,(246,140,96)),(.94,(248,190,152)),(1,(255,226,200))]
out = np.zeros(D.shape+(3,))
for (p0,c0),(p1,c1) in zip(stops, stops[1:]):
    sel = (D>=p0)&(D<=p1); t = ((D-p0)/(p1-p0))[...,None]
    out[sel] = (np.array(c0)*(1-t)+np.array(c1)*t)[sel]
img = Image.fromarray(out.astype(np.uint8))
img = img.resize((img.width*2, img.height*2), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 30, 3))
img.putalpha(Image.fromarray((A*255).astype(np.uint8)).resize(img.size, Image.LANCZOS))
img.save(out_path, optimize=True)
print(img.size)
