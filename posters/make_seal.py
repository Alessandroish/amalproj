import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
P='/home/user/amalproj/posters/'
bg=cv2.imread(P+'bg_dossier.png').astype(np.float32);ref=cv2.imread(P+'ref6.jpg').astype(np.float32)
H,W=bg.shape[:2];S=4  # supersample
cx,cy,R=840,813,47
yy,xx=np.mgrid[0:H,0:W];r=np.hypot(xx-cx,yy-cy)
# 1) flatten inner disc: inpaint emblem then keep low-freq shading + fine grain
inner=(r<R).astype(np.uint8)*255
sm=cv2.inpaint(ref.astype(np.uint8),inner,12,cv2.INPAINT_TELEA).astype(np.float32)
sm=cv2.GaussianBlur(sm,(0,0),7)
# gentle dish shading: slightly darker at top-left rim, lighter bottom-right (concave)
ang=np.arctan2(yy-cy,xx-cx);dish=np.clip(r/R,0,1)**2*np.cos(ang+2.3)*0.10
grain=np.random.default_rng(1).normal(0,3.0,(H,W,1)).astype(np.float32)
flat=sm*(1+dish[...,None])+grain
fi=cv2.GaussianBlur(inner.astype(np.float32),(0,0),1.5)[...,None]/255
out=flat*fi+bg*(1-fi)
# 2) raised lettering height map (supersampled)
BW=BH=2*R*S
img=Image.new('L',(BW,BH),0);d=ImageDraw.Draw(img)
f1=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',int(34*S))
f2=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',int(13.5*S))
d.text((BW/2,BH/2-7*S),'350',font=f1,fill=255,anchor='mm')
d.text((BW/2,BH/2+19*S),'ШТУК',font=f2,fill=255,anchor='mm')
# small ring + stars
d.ellipse([BW/2-41*S,BH/2-41*S,BW/2+41*S,BH/2+41*S],outline=255,width=int(1.6*S))
m=np.array(img).astype(np.float32)/255
h=cv2.GaussianBlur(m,(0,0),0.9*S)            # rounded relief
gy,gx=np.gradient(h*6)
L=np.array([-0.6,-0.7]);sh=(-(gx*L[0]+gy*L[1]))  # light from top-left
sh=cv2.resize(sh,(2*R,2*R),interpolation=cv2.INTER_AREA)
mm=cv2.resize(m,(2*R,2*R),interpolation=cv2.INTER_AREA)
hh=cv2.resize(h,(2*R,2*R),interpolation=cv2.INTER_AREA)
y0,x0=cy-R,cx-R
reg=out[y0:y0+2*R,x0:x0+2*R]
base=reg*(0.82+0.42*mm[...,None])              # top faces slightly brighter (polished)
lit=base*(1+2.1*sh[...,None])
spec=np.clip(sh,0,None)**1.5*260
lit=lit+spec[...,None]*np.array([0.75,0.92,1.0])
# soft contact shadow below-right of letters
shadow=cv2.GaussianBlur(np.roll(np.roll(mm,2,0),2,1),(0,0),1.2)
lit=lit*(1-0.45*np.clip(shadow-mm,0,1)[...,None])
disc=(np.hypot(*np.mgrid[-R:R,-R:R]+.5)<R-1).astype(np.float32)
disc=cv2.GaussianBlur(disc,(0,0),1)[...,None]
reg[:]=lit*disc+reg*(1-disc)
o8=np.clip(out,0,255).astype(np.uint8);hv=cv2.cvtColor(o8,cv2.COLOR_BGR2HSV)
rm=np.zeros((H,W),np.uint8);sub=(((hv[...,0]<10)|(hv[...,0]>170))&(hv[...,1]>110))[780:850,752:792];rm[780:850,752:792]=sub.astype(np.uint8)*255
rm=cv2.dilate(rm,np.ones((3,3),np.uint8),2);out=cv2.inpaint(o8,rm,5,cv2.INPAINT_TELEA).astype(np.float32)
cv2.imwrite(P+'bg_dossier2.png',np.clip(out,0,255).astype(np.uint8))
cv2.imwrite('/tmp/claude-0/-home-user-amalproj/7393960b-4a3c-5440-b7e3-6238436b5979/scratchpad/seal2.png',cv2.resize(np.clip(out,0,255).astype(np.uint8)[735:895,758:918],(480,480),interpolation=cv2.INTER_CUBIC))

# --- remove brand text from the pen barrel ---
im=cv2.imread(P+'bg_dossier2.png').astype(np.float32);hsv=cv2.cvtColor(im.astype(np.uint8),cv2.COLOR_BGR2HSV)
p=np.zeros((H,W),np.uint8);cv2.fillPoly(p,[np.array([(229,533),(247,538),(227,616),(209,611)])],255)
m=((p>0)&(hsv[...,2]>70)&(hsv[...,1]>25)).astype(np.uint8)
m=cv2.dilate(m,np.ones((3,3),np.uint8),2)&(p>0)
w=(1-m).astype(np.float32)
num=cv2.GaussianBlur(im*w[...,None],(0,0),4);den=cv2.GaussianBlur(w,(0,0),4)[...,None]+1e-6
fill=num/den+np.random.default_rng(2).normal(0,2,(H,W,1))
f=cv2.GaussianBlur(m.astype(np.float32),(0,0),1.2)[...,None]
cv2.imwrite(P+'bg_dossier2.png',np.clip(fill*f+im*(1-f),0,255).astype(np.uint8))

# --- remove middle sticky note (replaced by typed program) ---
im=cv2.imread(P+'bg_dossier2.png').astype(np.float32)
nm=np.zeros((H,W),np.uint8);cv2.fillPoly(nm,[np.array([(512,925),(640,884),(808,876),(834,1080),(814,1138),(562,1154)])],255)
nm=cv2.dilate(nm,np.ones((9,9),np.uint8))
sm=cv2.resize(im,(W//4,H//4),interpolation=cv2.INTER_AREA).astype(np.uint8);ms=cv2.resize(nm,(W//4,H//4),interpolation=cv2.INTER_NEAREST)
low=cv2.GaussianBlur(cv2.resize(cv2.inpaint(sm,ms,6,cv2.INPAINT_TELEA),(W,H),interpolation=cv2.INTER_CUBIC).astype(np.float32),(0,0),8)
src=im[1000:1110,330:520];hp=src-cv2.GaussianBlur(src,(0,0),5)
tile=np.tile(hp,(H//hp.shape[0]+1,W//hp.shape[1]+1,1))[:H,:W]
f=cv2.GaussianBlur(nm.astype(np.float32),(0,0),4)[...,None]/255
cv2.imwrite(P+'bg_dossier2.png',np.clip((low+tile)*f+im*(1-f),0,255).astype(np.uint8))

# --- glove layer above stamp + erase old stamp-hat remnant ---
im=cv2.imread(P+'bg_dossier2.png');hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
def poly(p):m=np.zeros((H,W),np.uint8);cv2.fillPoly(m,[np.array(p)],255);return m>0
hat=poly([(462,402),(548,414),(612,436),(606,505),(495,508),(493,480),(479,454),(458,428)])
region=poly([(290,320),(560,320),(560,530),(290,530)])
red=((hsv[...,0]<12)|(hsv[...,0]>168))&(hsv[...,1]>110)&(hsv[...,2]>40)
gm=(red&region&~hat).astype(np.uint8)*255
gm=cv2.morphologyEx(gm,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
n,l,st,_=cv2.connectedComponentsWithStats(gm);keep=np.zeros_like(gm)
for i in range(1,n):
    if st[i][4]>800:keep[l==i]=255
cnts,_=cv2.findContours(keep,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE);cv2.drawContours(keep,cnts,-1,255,-1)
keep[hat]=0
a=cv2.GaussianBlur(keep,(0,0),0.9)
g=cv2.cvtColor(im,cv2.COLOR_BGR2BGRA);g[...,3]=a;cv2.imwrite(P+'glove_layer.png',g)
# erase hat remnant (outside glove) with kraft
hm=(hat&(keep==0)).astype(np.uint8)*255;hm=cv2.dilate(hm,np.ones((5,5),np.uint8))&~cv2.dilate(keep,np.ones((3,3),np.uint8))
imf=im.astype(np.float32)
sm=cv2.resize(im,(W//4,H//4),interpolation=cv2.INTER_AREA);ms=cv2.resize(cv2.dilate(hm|keep,np.ones((7,7),np.uint8)),(W//4,H//4),interpolation=cv2.INTER_NEAREST)
low=cv2.GaussianBlur(cv2.resize(cv2.inpaint(sm,ms,5,cv2.INPAINT_TELEA),(W,H),interpolation=cv2.INTER_CUBIC).astype(np.float32),(0,0),5)
src=imf[1000:1110,330:520];hp=src-cv2.GaussianBlur(src,(0,0),5)
tile=np.tile(hp,(H//hp.shape[0]+1,W//hp.shape[1]+1,1))[:H,:W]
f=cv2.GaussianBlur(hm.astype(np.float32),(0,0),1.5)[...,None]/255
cv2.imwrite(P+'bg_dossier2.png',np.clip((low+tile)*f+imf*(1-f),0,255).astype(np.uint8))
