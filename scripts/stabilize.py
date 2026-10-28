#!/usr/bin/env python3
# Clear the start-up event popups until the bare main screen shows (Nick, 2026-10-28: "stable" = no popup).
# usage: D=<serial> scripts/stabilize.py      (called by boot.sh after Start; game already past the Start button)
# Each popup: tick "Do not remind me today" if it has one, then tap its X (top-right grey-blue square, white cross).
# exit 0 = main screen clear, 1 = popup it can't close (screenshot v_stabilize.png) -> close it by hand.
# Popup open = main screen's blue Recruit icon dimmed (0,158,230 -> ~0,33,50 under Dino's anniversary popup).
import time
from flow import find, grab, ocr, tap_text
from tap import tap as tap_wait

near = lambda p, c, tol=40: all(abs(a - b) <= tol for a, b in zip(p, c))
def is_main(im): return near(im.getpixel((92, 1788)), (0, 158, 230))


def close_x(im):
    """Centre of the popup's X button: the 64px block (right side, upper half) with the most white cross pixels that also
    touches the grey-blue frame. Frame-only blocks have <=34/256 white, the X ~80 (Dino anniversary popup, 2026-10-28)."""
    best, pos = 0, None
    for y0 in range(80, 1000, 16):
        for x0 in range(700, 1016, 16):
            ring = white = 0
            for y in range(y0, y0 + 64, 4):
                for x in range(x0, x0 + 64, 4):
                    p = im.getpixel((x, y))
                    ring += near(p, (115, 125, 156), 22); white += near(p, (255, 253, 255), 12)
            if ring >= 10 and white >= 50 and white > best: best, pos = white, (x0 + 32, y0 + 32)
    return pos


def main():
    for n in range(10):  # ponytail: ~3 stacked popups seen at most; 10 is a hard stop
        im = grab()
        if is_main(im):
            time.sleep(1.5)                                   # popups slide in late: confirm once more
            if is_main(grab()): print(f'stable ({n} popups closed)'); return 0
            continue
        boxes = ocr(im)
        if find(boxes, r'Do not remind me today'): tap_text(r'Do not remind me today', boxes=boxes); time.sleep(0.5)
        x = close_x(grab())
        if not x: break
        tap_wait(*x); time.sleep(1)
    grab().resize((540, 960)).save('v_stabilize.png'); print('popup not closable; stop (screenshot v_stabilize.png)'); return 1


if __name__ == '__main__':
    raise SystemExit(main())
