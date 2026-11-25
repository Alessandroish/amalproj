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

# --- glove layer above stamp (taken from the untouched original photo) + erase old stamp-hat ---
im=cv2.imread(P+'bg_dossier2.png');orig=cv2.imread(P+'ref6.jpg')
hsv=cv2.cvtColor(orig,cv2.COLOR_BGR2HSV)
def poly(p):m=np.zeros((H,W),np.uint8);cv2.fillPoly(m,[np.array(p)],255);return m>0
hat=poly([(452,392),(528,421),(552,408),(578,414),(602,425),(628,452),(624,478),(570,472),(520,480),(496,486),(491,468),(470,430),(461,413)])
pom=np.zeros((H,W),np.uint8);cv2.circle(pom,(430,512),19,255,-1);hat|=pom>0
region=poly([(40,40),(580,40),(580,540),(40,540)])
red=((hsv[...,0]<14)|(hsv[...,0]>165))&(hsv[...,1]>90)&(hsv[...,2]>35)
gm=(red&region&~hat).astype(np.uint8)*255
gm=cv2.morphologyEx(gm,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
n,l,st,_=cv2.connectedComponentsWithStats(gm);keep=np.zeros_like(gm)
for i in range(1,n):
    if st[i][4]>3000:keep[l==i]=255
cnts,_=cv2.findContours(keep,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE);cv2.drawContours(keep,cnts,-1,255,-1)
keep[hat]=0
keep[poly([(325,492),(455,492),(455,548),(325,548)])&~(red&(hsv[...,2]>60))]=0
keep=cv2.morphologyEx(keep,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
a=cv2.GaussianBlur(keep,(0,0),0.8)
dn=(hsv[...,2]<110)&~red
a2=cv2.GaussianBlur(cv2.erode(keep,np.ones((5,5),np.uint8)),(0,0),5)
a=np.where(dn,np.minimum(a,a2),a).astype(np.uint8)
g=cv2.cvtColor(orig,cv2.COLOR_BGR2BGRA);g[...,3]=a;cv2.imwrite(P+'glove_layer.png',g)
hm=((hat|poly([(452,392),(640,392),(640,528),(436,528),(436,500)])|poly([(330,505),(440,505),(440,540),(330,540)]))&(keep==0)).astype(np.uint8)*255;hm=hm&~cv2.dilate(keep,np.ones((3,3),np.uint8))
imf=im.astype(np.float32)
sm=cv2.resize(im,(W//4,H//4),interpolation=cv2.INTER_AREA);ms=cv2.resize(cv2.dilate(hm|keep,np.ones((7,7),np.uint8)),(W//4,H//4),interpolation=cv2.INTER_NEAREST)
low=cv2.GaussianBlur(cv2.resize(cv2.inpaint(sm,ms,5,cv2.INPAINT_TELEA),(W,H),interpolation=cv2.INTER_CUBIC).astype(np.float32),(0,0),5)
src=imf[1000:1110,330:520];hp=src-cv2.GaussianBlur(src,(0,0),5)
tile=np.tile(hp,(H//hp.shape[0]+1,W//hp.shape[1]+1,1))[:H,:W]
f=cv2.GaussianBlur(hm.astype(np.float32),(0,0),1.5)[...,None]/255
cv2.imwrite(P+'bg_dossier2.png',np.clip((low+tile)*f+imf*(1-f),0,255).astype(np.uint8))

# --- rebuild clean paper under the stamp/fingers ---
im=cv2.imread(P+'bg_dossier2.png').astype(np.float32);orig=cv2.imread(P+'ref6.jpg').astype(np.float32)
area=poly([(312,470),(372,408),(520,378),(705,418),(712,650),(312,650)])
ring=cv2.dilate(area.astype(np.uint8),np.ones((41,41),np.uint8))>0
hsvc=cv2.cvtColor(im.astype(np.uint8),cv2.COLOR_BGR2HSV)
paper=ring&~area&(hsvc[...,0]>=8)&(hsvc[...,0]<=30)&(hsvc[...,1]>40)&(hsvc[...,2]>120)
ys,xs=np.nonzero(paper);X=np.stack([np.ones_like(xs),xs,ys,xs*xs,ys*ys,xs*ys],1).astype(np.float64)/1.0
X[:,1:3]/=1000;X[:,3:]/=1e6
coef=[np.linalg.lstsq(X,im[ys,xs,c],rcond=None)[0] for c in range(3)]
yy,xx=np.mgrid[0:H,0:W];A=np.stack([np.ones_like(xx),xx/1000,yy/1000,xx*xx/1e6,yy*yy/1e6,xx*yy/1e6],-1)
low=np.stack([A@c for c in coef],-1).astype(np.float32)
src=orig[1005:1105,325:515];hp=src-cv2.GaussianBlur(src,(0,0),2.5)
nz=cv2.GaussianBlur(np.random.default_rng(7).normal(0,1,(H,W)).astype(np.float32),(0,0),14);nz=nz/nz.std()*5
t=np.concatenate([hp,hp[:,::-1]],1);t=np.concatenate([t,t[::-1]],0)
tile=np.tile(t,(H//t.shape[0]+1,W//t.shape[1]+1,1))[:H,:W]
fill=low+tile*.9+nz[...,None]*np.array([.6,.8,1.0],np.float32)
f=cv2.GaussianBlur(area.astype(np.float32),(0,0),6)[...,None]
cv2.imwrite(P+'bg_dossier2.png',np.clip(fill*f+im*(1-f),0,255).astype(np.uint8))

# --- final cleanup around fingertips: stray streaks, red slivers, pale/red halo ---
im=cv2.imread(P+'bg_dossier2.png');hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
ga=cv2.imread(P+'glove_layer.png',cv2.IMREAD_UNCHANGED)[...,3]>40
zone=poly([(318,455),(450,388),(620,410),(640,600),(318,600)])
paperish=cv2.GaussianBlur(zone.astype(np.float32),(0,0),1)>0
red=((hsv[...,0]<12)|(hsv[...,0]>165))&(hsv[...,1]>70)
dark=hsv[...,2]<120
ring=cv2.dilate(ga.astype(np.uint8),np.ones((13,13),np.uint8))>0
bad=zone&~ga&(poly([(452,388),(500,388),(505,440),(455,438)])|(red|dark)|(ring&(hsv[...,1]>40)&((hsv[...,0]<8)|(hsv[...,0]>160))))
bad=cv2.dilate(bad.astype(np.uint8)*255,np.ones((5,5),np.uint8))&~(ga.astype(np.uint8)*255)
r=cv2.inpaint(im,bad,7,cv2.INPAINT_TELEA).astype(np.float32)
nz=np.random.default_rng(5).normal(0,3,(H,W,1)).astype(np.float32)
f=cv2.GaussianBlur(bad.astype(np.float32),(0,0),1.2)[...,None]/255
cv2.imwrite(P+'bg_dossier2.png',np.clip((r+nz)*f+im*(1-f),0,255).astype(np.uint8))

# --- flat paper fill for small leftover patches next to fingertips ---
im=cv2.imread(P+'bg_dossier2.png').astype(np.float32)
ga=cv2.imread(P+'glove_layer.png',cv2.IMREAD_UNCHANGED)[...,3]>20
pm=(poly([(450,386),(508,386),(512,442),(452,440)])|poly([(318,478),(470,470),(520,478),(520,505),(470,548),(318,548)]))&~cv2.dilate(ga.astype(np.uint8),np.ones((3,3),np.uint8)).astype(bool)
ref=im[440:470,520:600].reshape(-1,3);col=np.median(ref,0)
src=im[560:660,420:560];hp=src-cv2.GaussianBlur(src,(0,0),3)
t=np.concatenate([hp,hp[:,::-1]],1);t=np.concatenate([t,t[::-1]],0);tile=np.tile(t,(H//t.shape[0]+1,W//t.shape[1]+1,1))[:H,:W]
fill=col+tile*.8
f=cv2.GaussianBlur(pm.astype(np.float32),(0,0),3)[...,None]
cv2.imwrite(P+'bg_dossier2.png',np.clip(fill*f+im*(1-f),0,255).astype(np.uint8))

# --- variant B: put the middle sticky note back (shifted down 60px) ---
im=cv2.imread(P+'bg_dossier2.png').astype(np.float32);old=cv2.imread(P+'bg_dossier.png').astype(np.float32)
nm=np.zeros((H,W),np.uint8);cv2.fillPoly(nm,[np.array([(512,925),(640,884),(808,876),(834,1080),(814,1138),(562,1154)])],255)
nm=cv2.dilate(nm,np.ones((15,15),np.uint8))
dy=60;M=np.float32([[1,0,0],[0,1,dy]])
oldS=cv2.warpAffine(old,M,(W,H));nmS=cv2.warpAffine(nm,M,(W,H))
f=cv2.GaussianBlur(nmS.astype(np.float32),(0,0),3)[...,None]/255
cv2.imwrite(P+'bg_dossier2_note.png',np.clip(oldS*f+im*(1-f),0,255).astype(np.uint8))

# --- remove the wax seal completely (both variants) ---
for name in ['bg_dossier2.png','bg_dossier2_note.png']:
    im=cv2.imread(P+name);imf=im.astype(np.float32)
    sm_=np.zeros((H,W),np.uint8);cv2.circle(sm_,(838,815),80,255,-1)
    s4=cv2.resize(im,(W//2,H//2),interpolation=cv2.INTER_AREA);m4=cv2.resize(sm_,(W//2,H//2),interpolation=cv2.INTER_NEAREST)
    low=cv2.GaussianBlur(cv2.resize(cv2.inpaint(s4,m4,8,cv2.INPAINT_TELEA),(W,H),interpolation=cv2.INTER_CUBIC).astype(np.float32),(0,0),3)
    src=imf[600:700,580:700];hp=src-cv2.GaussianBlur(src,(0,0),3)
    t=np.concatenate([hp,hp[:,::-1]],1);t=np.concatenate([t,t[::-1]],0);tile=np.tile(t,(H//t.shape[0]+1,W//t.shape[1]+1,1))[:H,:W]
    f=cv2.GaussianBlur(sm_.astype(np.float32),(0,0),4)[...,None]/255
    cv2.imwrite(P+name,np.clip((low+tile*.8)*f+imf*(1-f),0,255).astype(np.uint8))
