#!/usr/bin/env python3
# Offline check of poseidon.ships() / lock() (no device). usage: python3 scripts/test_poseidon.py
import os, sys
os.environ.setdefault('D', 'test')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
import poseidon

im = Image.new('RGB', (1080, 1920), (40, 120, 200))
d = ImageDraw.Draw(im)
def hearts(cx, cy, red):  # 3 hearts ~260 px above the name, like the rowboats
    for i, r in enumerate(red): d.rectangle((cx - 78 + 58 * i, cy - 270, cx - 42 + 58 * i, cy - 236), fill=(255, 0, 74) if r else (175, 190, 215))
hearts(208, 1582, [1, 0, 0]); hearts(540, 1540, [0, 0, 0]); hearts(872, 1082, [1, 1, 1])
boxes = [(140, 1568, 120, 30, 'MoMo -'), (170, 1616, 100, 30, '1657k'),        # alive (1 red)
         (460, 1522, 150, 36, 'Qwerty.tm'), (500, 1566, 100, 32, '1671k'),     # sunk (all grey)
         (810, 1062, 124, 40, 'raphi.sx'), (840, 1110, 104, 32, '1685k'),      # alive
         (8, 606, 266, 40, 'Contribute 1854k'),                                # merged box -> dropped
         (60, 500, 100, 30, 'Lord Eric'), (80, 548, 100, 30, '5907k')]         # behind the left buttons -> dropped
got = {s[1]: s for s in poseidon.ships(boxes, im)}
assert set(got) == {'MoMo -', 'Qwerty.tm', 'raphi.sx'}, got
assert got['MoMo -'][4] and got['raphi.sx'][4] and not got['Qwerty.tm'][4], got
assert got['MoMo -'][0] == 1657 and sorted(s for s in got.values() if s[4])[0][1] == 'MoMo -'
assert poseidon.CP.match('7.4M') and not poseidon.CP.match('Battling: 09:44')

poseidon.LOCKS = os.path.join('/tmp', f'poseidon-test-{os.getpid()}')
a = poseidon.lock('MoMo'); assert a and poseidon.lock('momo') is None   # second account can't take it
os.utime(a, (0, 0)); assert poseidon.lock('MoMo')                       # stale lock is taken over
print('ok')
