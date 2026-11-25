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
f1=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',int(30*S))
f2=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',int(11.5*S))
d.text((BW/2,BH/2-6*S),'350',font=f1,fill=255,anchor='mm')
d.text((BW/2,BH/2+18*S),'ШТУК',font=f2,fill=255,anchor='mm')
# small ring + stars
d.ellipse([BW/2-41*S,BH/2-41*S,BW/2+41*S,BH/2+41*S],outline=255,width=int(1.6*S))
m=np.array(img).astype(np.float32)/255
h=cv2.GaussianBlur(m,(0,0),1.6*S)            # rounded relief
gy,gx=np.gradient(h*6)
L=np.array([-0.6,-0.7]);sh=(-(gx*L[0]+gy*L[1]))  # light from top-left
sh=cv2.resize(sh,(2*R,2*R),interpolation=cv2.INTER_AREA)
mm=cv2.resize(m,(2*R,2*R),interpolation=cv2.INTER_AREA)
hh=cv2.resize(h,(2*R,2*R),interpolation=cv2.INTER_AREA)
y0,x0=cy-R,cx-R
reg=out[y0:y0+2*R,x0:x0+2*R]
base=reg*(1+0.18*mm[...,None])              # top faces slightly brighter (polished)
lit=base*(1+1.6*sh[...,None])
spec=np.clip(sh,0,None)**1.5*260
lit=lit+spec[...,None]*np.array([0.75,0.92,1.0])
# soft contact shadow below-right of letters
shadow=cv2.GaussianBlur(np.roll(np.roll(mm,2,0),2,1),(0,0),1.2)
lit=lit*(1-0.28*np.clip(shadow-mm,0,1)[...,None])
disc=(np.hypot(*np.mgrid[-R:R,-R:R]+.5)<R-1).astype(np.float32)
disc=cv2.GaussianBlur(disc,(0,0),1)[...,None]
reg[:]=lit*disc+reg*(1-disc)
o8=np.clip(out,0,255).astype(np.uint8);hv=cv2.cvtColor(o8,cv2.COLOR_BGR2HSV)
rm=np.zeros((H,W),np.uint8);sub=(((hv[...,0]<10)|(hv[...,0]>170))&(hv[...,1]>110))[780:850,752:792];rm[780:850,752:792]=sub.astype(np.uint8)*255
rm=cv2.dilate(rm,np.ones((3,3),np.uint8),2);out=cv2.inpaint(o8,rm,5,cv2.INPAINT_TELEA).astype(np.float32)
cv2.imwrite(P+'bg_dossier2.png',np.clip(out,0,255).astype(np.uint8))
cv2.imwrite('/tmp/claude-0/-home-user-amalproj/7393960b-4a3c-5440-b7e3-6238436b5979/scratchpad/seal2.png',cv2.resize(np.clip(out,0,255).astype(np.uint8)[735:895,758:918],(480,480),interpolation=cv2.INTER_CUBIC))
