#!/usr/bin/env python3
# usage: D=<serial> scripts/grocery.py  (Grocery Daily Specials tab must be open).
# Grocery: claim every top-row chest whose button says Free. Green Free (pass accounts) = instant; the grey "▶ Free"
# ad button (no Play Pass, xFaktor 2026-11-08 — Nick: watch the ads) -> popup's green Free -> video ad
# (flow.watch_ad) -> Congratulations popup. Gem-priced buttons are never tapped (not green, no "Free" text).
import subprocess, time, os, sys
from PIL import Image
from flow import find, ocr, watch_ad
D=os.environ['D']; T=os.path.join(os.path.dirname(os.path.abspath(__file__)),'tap.py')
def shot(o='g.png'): subprocess.run([T,'-o',o],env=os.environ); return Image.open(o).convert('RGB')
def green(p): return p[1]>180 and p[0]<150 and p[2]<90
def tap(x,y): subprocess.run(['adb','-s',D,'shell','input','tap',str(x),str(y)])
def popup_green_y(p):   # scan popup column for the green Free button
    for y in range(500,820,4):
        if green(p.getpixel((200,y))): return y+12
idle=0; ad_fail=0
while idle<8:   # ~12 s of no Free button (cooldowns are 5–8 s) = done
    im=shot(); got=False; boxes=None
    for x in (82,207,332,457):
        ad=False
        if not green(im.getpixel((x,436))):
            boxes = boxes or ocr(im)                   # 540-wide coords; "Free" text on a non-green button = ad chance
            if not find(boxes, r'Free$', (x-55,405,x+55,470)): continue   # OCR gives '} Free' (the ▶ icon) on chest 3 (xFaktor 2026-11-08)
            ad=True
        subprocess.run([T,f'{x*2},893','-o','p.png'],env=os.environ); p=Image.open('p.png').convert('RGB'); y=popup_green_y(p)
        if not y: print('popup has no green Free; closing',x,flush=True); subprocess.run([T,'540,1850','-o','g.png'],env=os.environ); break
        if not ad:
            subprocess.run([T,f'540,{y*2}','540,1850','-o','g.png'],env=os.environ); print('claimed',x,flush=True); got=True; break
        tap(540,y*2)
        if not watch_ad(): print('ad did not close; stop',flush=True); sys.exit(1)
        for _ in range(4):                              # reward popup can lag the ad's close by a second or two
            time.sleep(1.5); b=ocr()
            if find(b, r'Tap anywhere to close|Congratulations'): break
        if find(b, r'Tap anywhere to close|Congratulations'):
            tap(540,1850); print('claimed (ad)',x,flush=True); got=True; ad_fail=0
        else:
            ad_fail+=1; print('ad closed but no reward popup',x,flush=True); tap(540,1850)   # chest popup still up -> close
            if ad_fail>=2: print('2 ads without reward; stop',flush=True); sys.exit(1)
        break
    if got: idle=0
    elif find(ocr(im), r'Tap anywhere to close'):   # reward popup that came up after the dismiss tap dims every Free
        tap(540,1850); time.sleep(1)                 # button -> looked idle, quit with 8 chests left (Dino 2026-11-01)
    else: idle+=1; time.sleep(1.5)
print('done')
