# Sharp banknote-style engraving of the head of Hermes (Venice, Museo archeologico nazionale), frontal.
# Source: File:(Venice) Ancient Roman busts in the Museo archeologico nazionale - Head of Hermes.jpg
#   (Didier Descouens, Wikimedia Commons, public domain); 3840px thumbnail:
#   upload.wikimedia.org/wikipedia/commons/thumb/f/fc/<name>/3840px-<name>
# Band crop: brow, eyes, nose, moustache. Lines follow the form; crosshatching in the shadows.
# Usage: python3 engrave_hermes_venice.py venice-3840.jpg [engraving-hermes-venice.png] [period px, default 8]
import sys
from PIL import Image, ImageFilter
import numpy as np
im = Image.open(sys.argv[1]).convert('L')
out_path = sys.argv[2] if len(sys.argv) > 2 else 'engraving-hermes-venice.png'
p = float(sys.argv[3]) if len(sys.argv) > 3 else 8.0
K = im.width / 590                                       # crop traced on a 590px-wide preview
im = im.crop(tuple(int(v*K) for v in (62, 130, 528, 450)))
S = 1.3
im = im.resize((int(im.width*S), int(im.height*S)), Image.LANCZOS)
L = np.asarray(im).astype(np.float32)/255
def blur(x, r): return np.asarray(Image.fromarray((np.clip(x,0,1)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(np.float32)/255
T = blur(L, 2.6)
T = T + .7*(T - blur(L, 22)) + 1.1*(T - blur(L, 110))      # carve the forms: white marble is flat otherwise
lo, hi = np.percentile(T, [4, 96]); T = np.clip((T - lo)/(hi - lo), 0, 1)
T = np.clip(T*1.15 - .05, 0, 1) ** 1.35            # bright marble, deep sockets
dark = 1 - T
H, W = T.shape; yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
G = blur(L, 50)
ph = yy + 90*G*p/13 + 5*np.sin(xx/300.)
d1 = np.abs((ph % p) - p/2)
ink = np.clip(p/2*np.clip(dark*1.08, 0, 1)**.8 - d1 + .8, 0, 1)
q = p*11/13
ph2 = (xx*.5 + yy*.87) + 50*G
d2 = np.abs((ph2 % q) - q/2)
ink2 = np.clip(q/2*np.clip((dark - .5)/.5, 0, 1) - d2 + .6, 0, 1) * np.clip((dark - .5)/.08, 0, 1)
ink = np.maximum(ink, ink2)
paper = np.array([236, 233, 226.], np.float32); inkc = np.array([22, 20, 20.], np.float32)
rgb = paper*(1 - ink[..., None]) + inkc*ink[..., None]
Image.fromarray(rgb.astype(np.uint8)).save(out_path, optimize=True); print(W, H)
