#!/usr/bin/env python3
# Play Storm Battlefield matches until tickets run out. Arena screen (yellow "Start Match") must be open.
# usage: D=<serial> scripts/storm.py   — polls every ~0.5 s, so a match costs only its real length.
import os, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tap import grab
D = os.environ['D']
def arena(im): p = im.getpixel((400, 1580)); return p[0] > 200 and p[1] > 150 and p[2] < 80  # Start Match yellow
def tap(x, y): subprocess.run(['adb', '-s', D, 'shell', 'input', 'tap', str(x), str(y)])
n = 0
while n < 20:
    if not arena(grab()):
        print('not on arena screen; stop'); break
    before = grab().getpixel((560, 1430))          # ticket counter digit
    tap(540, 1610); t0 = time.time(); time.sleep(1.5)
    im = grab()
    if arena(im) and im.getpixel((560, 1430)) == before:
        print('Start Match did nothing (0 tickets?); done'); break
    g = im.getpixel((350, 1274))                    # 0 tickets -> game opens the "+" popup by itself
    if abs(g[0] - g[1]) < 20 and abs(g[1] - g[2]) < 20 and 150 < g[0] < 220:   # grey Free button
        tap(100, 1150); print('out of tickets and free video chances; done'); break
    while time.time() - t0 < 150:
        im = grab()
        if arena(im): break
        if time.time() - t0 > 4: tap(540, 120)      # dismiss Victory/Defeat once it shows
        time.sleep(0.5)
    n += 1; print(f'match {n}: {time.time() - t0:.0f}s', flush=True)
