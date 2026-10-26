# Refresh a Fishing daily order until it has >=4 diamonds (Mythic+). Daily Order dialog must be open.
# Stops on any unexpected pixel (popup, out of tickets). Run from a scratch dir: writes s.png.
# usage: fish.py ROW MAXTRIES  -> refresh order ROW (1-3) until >=4 diamonds; stops on any unexpected pixel
import subprocess, sys, time
from PIL import Image
D='127.0.0.1:26625'
row=int(sys.argv[1]); maxn=int(sys.argv[2])
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
    n=count()
    print(i,n,flush=True)
    if n is None or n>=4 or i==maxn: break
    subprocess.run(f'adb -s {D} shell input tap 849 {BY}',shell=True); time.sleep(1.5)
