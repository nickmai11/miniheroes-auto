#!/usr/bin/env python3
# Refresh a Fishing daily order until it has >=MIN diamonds. Daily Order dialog must be open.
# Confirms the "Confirm to refresh orders? Cost x1" popup, never ticks "Do not remind me today" (Nick, 2026-10-29).
# "The order is of high quality" popup = we're refreshing a good order by mistake: Cancel + WARN, stop.
# Stops on any other unexpected pixel (out of tickets). Run from a scratch dir: writes s.png.
# usage: D=<serial> fish_orders.py ROW MAXTRIES [MIN=4]  -> refresh order ROW (1-3) until >=MIN diamonds (config min_order_diamonds)
import os, re, subprocess, sys, time
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flow import ocr
D=os.environ['D']
row=int(sys.argv[1]); maxn=int(sys.argv[2]); mn=int(sys.argv[3]) if len(sys.argv)>3 else 4
Y={1:567,2:921,3:1275}[row]; BY={1:704,2:1058,3:1412}[row]
XS=[int(x/0.469) for x in (297,331,365,399,432)]
def count(retry=3):
    for _ in range(retry):
        n=count1()
        if n is not None: return n
        time.sleep(1)
    return None
def count1():
    subprocess.run(f'adb -s {D} exec-out screencap -p > s.png',shell=True)
    im=Image.open('s.png').convert('RGB'); n=0
    for x in XS:
        p=im.getpixel((x,Y))
        if p[0]>200 and p[1]>150: n+=1
        elif p==(58,85,115): pass
        else: return None
    return n
for i in range(maxn+1):
    n=count1()
    if n is None:
        txt=' '.join(b[4] for b in ocr(Image.open('s.png')))
        if re.search(r'high quality', txt):    # refreshing an order the game calls good = we misread a row (Nick, 2026-10-29)
            subprocess.run(f'adb -s {D} shell input tap 320 1212',shell=True); time.sleep(1.5)   # Cancel
            print(f'WARN row {row}: "order is of high quality" popup - cancelled, row left as is',flush=True); break
        if re.search(r'Confirm to refresh', txt):
            subprocess.run(f'adb -s {D} shell input tap 757 1211',shell=True); time.sleep(1.5)   # Confirm
        n=count()
    print(i,n,flush=True)
    if n is None or n>=mn or i==maxn: break
    subprocess.run(f'adb -s {D} shell input tap 849 {BY}',shell=True); time.sleep(1.5)
