#!/usr/bin/env python3
"""Tap device coords and wait only as long as the screen needs, then save a screenshot.

usage: D=127.0.0.1:26625 scripts/tap.py [x,y ...] [-o out.png] [--until x,y,r,g,b[,tol] | --until-text REGEX] [--timeout s]
  - each tap: waits until the screen changes, then until it settles (max ~4 s), instead of a fixed sleep
  - no taps: just screenshots
  - --until: after the taps, poll (~0.3 s) until device pixel (x,y) is within tol (default 40) of r,g,b,
    e.g. a button that reappears when a battle ends; exits 1 on --timeout (default 120 s)
  - --until-text: poll (OCR, ~0.5 s) until some on-screen text matches REGEX (re.search), e.g. the next screen's
    title; prints that screen's OCR text either way (often enough to decide without reading the png);
    exits 1 on --timeout (default 10 s). For screens with no mapped pixel (Nick, 2026-10-29: helpers used
    --until on 1 of 493 taps — the doc had almost no pixels).
  - writes the last screenshot to -o (default ./v.png), downscaled to -w px wide (default 540; 270 is ~4x
    cheaper to read — use it for navigation, 540 only to read small text). Tap coords are always device coords.
"""
import io, os, subprocess, sys, time
from PIL import Image, ImageChops, ImageStat

D = os.environ['D']
MAX_WAIT = float(os.environ.get('MAX_WAIT', 4))
SETTLE_MAX = float(os.environ.get('SETTLE_MAX', 1.2))  # after a change, settle for at most this long
NO_CHANGE = float(os.environ.get('NO_CHANGE', 1.5))   # nothing changed by then -> tap had no visible effect, stop waiting
CHANGED, SETTLED = 6.0, 3.0  # mean abs diff on a 54x96 grey thumb; idle animations stay below CHANGED


def grab():
    for attempt in range(3):  # screencap sometimes hangs with several workers on one adb server
        try:
            raw = subprocess.run(['adb', '-s', D, 'exec-out', 'screencap'], capture_output=True, timeout=10).stdout
            break
        except subprocess.TimeoutExpired:
            if attempt == 2: raise
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
            elif time.time() - t0 > NO_CHANGE:
                return im
        elif diff(cur, prev) < SETTLED or time.time() - tc > SETTLE_MAX:
            return im
        prev = cur
    return im


def opt(argv, name, default=None):
    if name in argv:
        i = argv.index(name); v = argv[i + 1]; del argv[i:i + 2]; return v
    return default


def main(argv):
    out = opt(argv, '-o', 'v.png'); w = int(opt(argv, '-w', 540))
    until = opt(argv, '--until'); text = opt(argv, '--until-text')
    timeout = float(opt(argv, '--timeout', 10 if text else 120))
    im = None
    for t in argv:
        x, y = t.split(',')[:2]
        im = tap(int(x), int(y))
    ok = True
    if until:
        v = [int(n) for n in until.split(',')]; x, y, want, tol = v[0], v[1], v[2:5], (v[5] if len(v) > 5 else 40)
        t0 = time.time()
        while True:
            im = grab()
            # a screenshot can come back at the physical size right after boot (xFaktor 600x1080) -> keep polling
            if x < im.width and y < im.height and max(abs(a - b) for a, b in zip(im.getpixel((x, y)), want)) <= tol:
                break
            if time.time() - t0 > timeout:
                ok = False; break
            time.sleep(0.3)
    if text:
        import re; from flow import ocr, joined
        t0 = time.time()
        while True:
            im = grab(); boxes = ocr(im)
            if any(re.search(text, b[4]) for b in boxes):   # text shows while a screen still slides in (Adventure list,
                t1, prev = time.time(), thumb(im)              # 2026-10-29: next tap hit Beast Realm) -> let it settle too
                while time.time() - t1 < SETTLE_MAX:
                    time.sleep(0.2); im = grab(); cur = thumb(im)
                    if diff(cur, prev) < SETTLED: break
                    prev = cur
                break
            if time.time() - t0 > timeout: ok = False; break
            time.sleep(0.3)
        print(('' if ok else f'TIMEOUT waiting for {text!r}: ') + joined(boxes))
    im = im or grab()
    im.resize((w, w * 16 // 9)).save(out)
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main(sys.argv[1:])
