#!/usr/bin/env python3
# Floating Realm Guess (event screen, dice bottom right): pick the 1st / 2nd / 3rd tribe and Save. Free, no gems.
# usage: D=<serial> scripts/realm_guess.py ace purple kitchen   (main screen or the Floating Realm event screen)
# Same dialog as the Tribe Clash Guess (clash_guess.py does the picking: 3 banners, slot 1 filled first, names under
# the tiles, a scrolling list, Save, X); here the banner band for the picked names is wider and a "Match Result"
# popup can cover the event screen. Mapped on xFaktor 2026-11-05, 9 accounts that day. Ends on the main screen.
# exit 1 -> v_realm_guess.png.
import sys, time
from clash_guess import SLOTS, pick
from flow import Stop, find, joined, main, ocr, tap_wait, wait

BAND = (280, 760)                                           # banner area: a picked tribe's name shows there
FR_BANNER = (600, 400, 1080, 900)


def slot(boxes, rank):
    x0, x1 = SLOTS[rank]
    return ' '.join(t for x, y, w, h, t in boxes if x0 <= x + w // 2 <= x1 and BAND[0] <= y + h // 2 <= BAND[1]
                    and not t[:1].isdigit() and t != 'Guessing')


def run(picks):
    boxes = ocr()
    if not find(boxes, r'Please select a tribe'):
        if not find(boxes, r'^Guess$', (880, 1800, 1080, 1920)):          # main screen -> banner -> event screen
            boxes = wait(r'Floating Realm', 15, FR_BANNER)
            tap_wait(*find(boxes, r'Floating Realm', FR_BANNER)); boxes = wait(r'^Enter$|Match Result|Tap anywhere', 12)
        for _ in range(3):                                   # "Match Result" ranking popup over the event screen (5 accounts 2026-11-05)
            if not find(boxes, r'Match Result|Tap anywhere to close'): break
            tap_wait(540, 1486); time.sleep(1); boxes = ocr()
        g = find(boxes, r'^Guess$', (880, 1800, 1080, 1920))
        if not g: raise Stop(f'no Guess button: {joined(boxes)[:200]}')
        for i in (1, 2):
            tap_wait(g[0], g[1] - 50)
            try: boxes = wait(r'Please select a tribe', 4); break
            except Stop:
                if i == 2: raise
    pick(boxes, picks, slot)
    tap_wait(96, 1812); time.sleep(1.5)                     # event screen -> main


if __name__ == '__main__':
    if len(sys.argv) != 4: sys.exit('usage: realm_guess.py <1st> <2nd> <3rd>')
    main(run, sys.argv[1:])
