# usage: D=<serial> scripts/grocery.py  (Grocery Daily Specials tab must be open). Language-independent (colour-based).
# Grocery: claim any top-row chest whose button is green "Free" (gem-priced buttons aren't green); wait cooldowns.
import subprocess, time, os
from PIL import Image
D=os.environ['D']; T=os.path.join(os.path.dirname(os.path.abspath(__file__)),'tap.py')
def shot(o='g.png'): subprocess.run([T,'-o',o],env=os.environ); return Image.open(o).convert('RGB')
def green(p): return p[1]>180 and p[0]<150 and p[2]<90
def tap(x,y): subprocess.run(['adb','-s',D,'shell','input','tap',str(x),str(y)])
def popup_green_y(p):   # scan popup column for the green Free button
    for y in range(500,820,4):
        if green(p.getpixel((200,y))): return y+12
idle=0
while idle<4:
    im=shot(); got=False
    for x in (82,207,332,457):
        if green(im.getpixel((x,436))):
            tap(x*2,893); time.sleep(2.5); p=shot('p.png'); y=popup_green_y(p)
            if y: tap(540,y*2); time.sleep(2.5); tap(540,1850); time.sleep(1.5); print('claimed',x,flush=True); got=True
            else: print('popup has no green Free; closing',x,flush=True); tap(540,1850); time.sleep(1)
            break
    if got: idle=0
    else: idle+=1; time.sleep(3)
print('done')
