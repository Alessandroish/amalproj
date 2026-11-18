from PIL import Image, ImageFilter, ImageDraw, ImageChops
import numpy as np
im = Image.open('big.jpg').convert('RGB')
a = np.asarray(im).astype(float)
r,g,b = a[...,0],a[...,1],a[...,2]
mx = a.max(-1); mn = a.min(-1); sat = (mx-mn)/(mx+1)
m = (sat < .28) & (g - r < 14) & (mx > 40)
m[:, :600] = False; m[:, 1440:] = False; m[:400] = False; m[2260:] = False
mask = Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.MedianFilter(7))
mask = mask.filter(ImageFilter.MinFilter(9)).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.MinFilter(7))
# fill enclosed holes via floodfill of background from corner
pad = Image.new('L', (mask.width+2, mask.height+2), 0); pad.paste(mask, (1,1))
ImageDraw.floodfill(pad, (0,0), 128)
P = np.asarray(pad)[1:-1,1:-1]
filled = (P != 128)
mask = Image.fromarray((filled*255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.6))
box = (600,400,1440,2260)
mask = mask.crop(box); im = im.crop(box)
A = np.asarray(mask).astype(float)/255
src = im.copy(); src.putalpha(mask); src.save('/home/user/amalproj/poster/statue-source-cutout.png')

L = np.asarray(im.convert('L')).astype(float)/255
def blur(x, r): return np.asarray(Image.fromarray((np.clip(x,0,1)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(float)/255
# local contrast: bring out folds and carving
D = L + 0.55*(L - blur(L, 4)) + 0.9*(L - blur(L, 30))
# pseudo-normals from shading -> directional sun from upper-left
S = blur(L, 5)
gy, gx = np.gradient(S)
lx, ly = -0.75, -0.66
lam = np.clip(-(gx*lx + gy*ly) * 22, -1, 1)
D = D + 0.30*lam
# global light falloff: lit upper-left, deep shadow lower-right
H, W = L.shape; yy, xx = np.mgrid[0:H, 0:W]
fall = np.clip(1.10 - 0.95*np.clip(xx/W*.75 + yy/H*.65 - .2, 0, 1.2), .25, 1.25)
D = np.clip((D - .30) / .68, 0, 1.2) * fall
# rim light along left/top silhouette edge
edge = np.clip(A - blur(A, 9), 0, 1)
rim = edge * np.clip(1.2 - xx/W*1.6, 0, 1) * 0.7
D = np.clip(D + rim, 0, 1)
D = np.clip(D,0,1)**1.45
stops = [(0,(10,1,1)),(.18,(52,6,5)),(.40,(132,20,12)),(.62,(214,62,34)),(.80,(250,150,100)),(.92,(255,214,170)),(1,(255,246,232))]
out = np.zeros(D.shape+(3,))
for (p0,c0),(p1,c1) in zip(stops, stops[1:]):
    sel=(D>=p0)&(D<=p1); t=((D-p0)/(p1-p0))[...,None]
    out[sel]=(np.array(c0)*(1-t)+np.array(c1)*t)[sel]
img = Image.fromarray(out.astype(np.uint8))
S2 = 2
img = img.resize((img.width*S2, img.height*S2), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 35, 3))
img.putalpha(mask.resize(img.size, Image.LANCZOS))
img.save('/home/user/amalproj/poster/statue-justitia.png', optimize=True)
prev = Image.new('RGB', img.size, (40,4,4)); prev.paste(img, (0,0), img)
prev.resize((img.width//4, img.height//4)).save('relit_prev.jpg')
print(img.size)
