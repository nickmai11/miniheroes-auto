#!/usr/bin/env python3
"""Crystal Throne: D=<serial> scripts/ct_siege.py <node label> [Siege|Attack|March] [mx,my]
Minimap -> full map tap (mx,my, optional) -> find the node's label by OCR -> tap its building -> action button.
Prints OK / NO <why> + screen text. Then the one 20-gem Speed Up per move (only at price 20), ticking "Do not remind me today" on its tip."""
import re, sys, time
from flow import Stop, find, joined, ocr, tap, tap_wait, wait
name, act = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else 'Siege')
from flow import swipe
if find(ocr(), r'^Watchtower$'): tap_wait(92, 1810); time.sleep(0.8)       # full map open -> back to the battlefield
if len(sys.argv) > 3 and not find(ocr(), name):                            # drag x0,y0,x1,y1 to bring the node into view
    swipe(*map(int, sys.argv[3].split(',')), 500); time.sleep(1)
b = ocr(); p = find(b, name)
if not p: print('NO label', name, '|', joined(b)[:200]); sys.exit(1)
tap(p[0], p[1] - 150)                                        # building sits above its label
try: b = wait(rf'^{act}$', 3)
except Stop: print('NO popup |', joined(ocr())[:200]); sys.exit(1)
if find(b, r'Non-adjacent'): print('NO not adjacent |', joined(b)[:150]); sys.exit(1)
tap_wait(*find(b, rf'^{act}$')); time.sleep(0.5)
b = ocr()
su = find(b, r'^20 *Speed Up$|^Speed Up$')
# one 20-gem speed-up per move (Nick, 2026-11-05): price must read 20; tip popup -> tick "Do not remind me today" first
if su and find(b, r'(^|\D)20(\D|$)', (su[0] - 300, su[1] - 60, su[0] + 300, su[1] + 60)):   # price next to the button
    tap_wait(*su)
    try:
        b = wait(r'Current March Time|Do not remind', 2)
        t = find(b, r'Do not remind me today')
        if t: tap(t[0] - 160, t[1]); time.sleep(0.3)                  # the tick circle sits left of the label
        c = find(b, r'^20 *Speed Up$|Speed Up$', (0, 1000, 1080, 1300))
        if c: tap_wait(*c); print('SPED 20 gems', flush=True)
    except Stop: pass                                                  # no tip: the first tap already sped it up
    b = ocr()
print('OK' if find(b, r'Speed Up|Queue|Marching') else 'CHECK', '|', joined(b)[:200])
