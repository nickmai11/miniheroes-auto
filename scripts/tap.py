#!/usr/bin/env python3
"""Tap device coords and wait only as long as the screen needs, then save a screenshot.

usage: D=127.0.0.1:26625 scripts/tap.py [x,y ...] [-o out.png]
  - each tap: waits until the screen changes, then until it settles (max ~4 s), instead of a fixed sleep
  - no taps: just screenshots
  - writes the last screenshot to -o (default ./v.png), downscaled to 540 px wide
"""
import io, os, subprocess, sys, time
from PIL import Image, ImageChops, ImageStat

D = os.environ['D']
MAX_WAIT = float(os.environ.get('MAX_WAIT', 4))
SETTLE_MAX = float(os.environ.get('SETTLE_MAX', 1.2))  # after a change, settle for at most this long
CHANGED, SETTLED = 6.0, 3.0  # mean abs diff on a 54x96 grey thumb; idle animations stay below CHANGED


def grab():
    raw = subprocess.run(['adb', '-s', D, 'exec-out', 'screencap'], capture_output=True).stdout
    w, h = int.from_bytes(raw[0:4], 'little'), int.from_bytes(raw[4:8], 'little')
    return Image.frombuffer('RGBA', (w, h), raw[-w * h * 4:], 'raw', 'RGBA', 0, 1).convert('RGB')


def thumb(im):
    return im.convert('L').resize((54, 96))


def diff(a, b):
    return ImageStat.Stat(ImageChops.difference(a, b)).mean[0]


def tap(x, y):
    before = thumb(grab())
    subprocess.run(['adb', '-s', D, 'shell', 'input', 'tap', str(x), str(y)])
    t0, tc, prev = time.time(), None, before
    while time.time() - t0 < MAX_WAIT:
        im = grab(); cur = thumb(im)
        if tc is None:
            if diff(cur, before) > CHANGED:
                tc = time.time()
        elif diff(cur, prev) < SETTLED or time.time() - tc > SETTLE_MAX:
            return im
        prev = cur
    return im


def main(argv):
    out = 'v.png'
    if '-o' in argv:
        i = argv.index('-o'); out = argv[i + 1]; del argv[i:i + 2]
    im = None
    for t in argv:
        x, y = t.split(',')[:2]
        im = tap(int(x), int(y))
    im = im or grab()
    im.resize((540, 960)).save(out)


if __name__ == '__main__':
    main(sys.argv[1:])
