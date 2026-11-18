from PIL import Image, ImageFilter, ImageDraw
import numpy as np
im = Image.open('aug.jpg').convert('RGB')
a = np.asarray(im).astype(float); r,g,b = a[...,0],a[...,1],a[...,2]
m = (r - b > 10) | ((r+g+b)/3 > 200)
m[1890:] = False                       # drop pedestal
m[1300:, :760] = False                 # drop cupid
mask = Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.MedianFilter(5))
mask = mask.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9))
pad = Image.new('L', (mask.width+2, mask.height+2), 0); pad.paste(mask, (1,1))
ImageDraw.floodfill(pad, (0,0), 128)
mask = Image.fromarray(((np.asarray(pad)[1:-1,1:-1] != 128)*255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.4))
box = (120, 40, 1490, 1900)
mask = mask.crop(box); im = im.crop(box)
A = np.asarray(mask).astype(float)/255
L = np.asarray(im.convert('L')).astype(float)/255
def blur(x, r): return np.asarray(Image.fromarray((np.clip(x,0,1)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(float)/255
Ls = blur(L, 1.6)
D = Ls + 0.25*(Ls - blur(L, 4)) + 0.45*(Ls - blur(L, 25))      # crisp carving, smooth marble
H, W = L.shape; yy, xx = np.mgrid[0:H, 0:W]
# sun from upper-left: warm on face/arm/chest, deep shade lower-right
fall = np.clip(1.2 - 0.9*np.clip(xx/W*.55 + yy/H*.8 - .25, 0, 1.2), .2, 1.1)
D = np.clip((D - .22) / .70, 0, 1.2) * fall
edge = np.clip(A - blur(A, 7), 0, 1)
D = np.clip(D + edge*np.clip(1 - xx/W*1.5, 0, 1)*0.22, 0, 1) ** 1.4
stops = [(0,(8,1,1)),(.2,(48,5,4)),(.42,(125,18,11)),(.64,(205,55,30)),(.82,(246,140,96)),(.94,(248,190,152)),(1,(255,226,200))]
out = np.zeros(D.shape+(3,))
for (p0,c0),(p1,c1) in zip(stops, stops[1:]):
    sel=(D>=p0)&(D<=p1); t=((D-p0)/(p1-p0))[...,None]
    out[sel]=(np.array(c0)*(1-t)+np.array(c1)*t)[sel]
img = Image.fromarray(out.astype(np.uint8))
img = img.resize((img.width*2, img.height*2), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 30, 3))
img.putalpha(mask.resize(img.size, Image.LANCZOS))
img.save('/home/user/amalproj/poster/statue-augustus.png', optimize=True)
prev = Image.new('RGB', img.size, (40,4,4)); prev.paste(img,(0,0),img); prev.resize((img.width//5, img.height//5)).save('aug_prev.jpg')
print(img.size)
