#!/usr/bin/env python3
# Refresh a Fishing daily order until it has >=MIN diamonds. Daily Order dialog must be open.
# Confirms the "Confirm to refresh orders? Cost x1" popup, never ticks "Do not remind me today" (Nick, 2026-10-29).
# "The order is of high quality" popup = we're refreshing a good order by mistake: Cancel + WARN, stop.
# Out of scrolls = no Confirm popup after a Refresh tap -> prints NOSCROLL <refreshes done> (the caller buys via '+').
# Stops on any other unexpected pixel. Run from a scratch dir: writes s.png.
# usage: D=<serial> fish_orders.py ROW MAXTRIES [MIN=4]  -> refresh order ROW (1-3) until >=MIN diamonds (config min_order_diamonds)
import os, re, subprocess, sys, time
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flow import grab, near, ocr, tap
D=os.environ['D']
row=int(sys.argv[1]); maxn=int(sys.argv[2]); mn=int(sys.argv[3]) if len(sys.argv)>3 else 4
Y={1:567,2:921,3:1275}[row]; BY={1:704,2:1058,3:1412}[row]
XS=[int(x/0.469) for x in (297,331,365,399,432)]
def count1():
    im=grab(); im.save('s.png'); n=0   # grab(): 1080x1920 on every instance
    for x in XS:
        p=im.getpixel((x,Y))
        if p[0]>200 and p[1]>150: n+=1
        elif near(p,(58,85,115),8): pass   # not ==: an upscaled 900x1600 frame can be 1-2 off
        else: return None
    return n or None   # 0 diamonds is impossible (every order has >=1): a misread mid-animation (Cmajor 2026-10-29)
for i in range(maxn+1):
    for _ in range(4):                         # popups can show up >3 s after the Refresh tap (Cmajor/Chien Than 2026-10-29)
        n=count1()
        if n is not None: break
        txt=' '.join(b[4] for b in ocr(Image.open('s.png')))
        if re.search(r'high quality', txt):    # refreshing an order the game calls good = we misread a row (Nick, 2026-10-29)
            tap(320,1212); time.sleep(1.5)   # Cancel
            print(f'WARN row {row}: "order is of high quality" popup - cancelled, row left as is',flush=True); n='hq'; break
        if re.search(r'Confirm to refresh', txt):
            tap(757,1211)
        time.sleep(1.5)
    if n=='hq': break
    print(i,n,flush=True)
    if n is None or n>=mn or i==maxn: break
    tap(849,BY)
    # "Do not remind" is never ticked, so a scroll left = the Confirm popup shows. None in ~4 s = 0 scrolls: the tap did
    # nothing (Boudior 2026-11-14, no purchase popup either) -> NOSCROLL <refreshes done>, the caller buys via '+'
    for _ in range(8):
        if re.search(r'Confirm to refresh|high quality|Order Refresh Scroll', ' '.join(b[4] for b in ocr())): break
        time.sleep(0.5)
    else: print(f'NOSCROLL {i}',flush=True); break
