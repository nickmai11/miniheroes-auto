#!/usr/bin/env python3
# Floating Realm Guess (event screen, dice bottom right): pick the 1st / 2nd / 3rd tribe and Save. Free, no gems.
# usage: D=<serial> scripts/realm_guess.py ace purple kitchen   (main screen or the Floating Realm event screen)
# Same dialog as the Tribe Clash Guess (clash_guess.py: 3 banners, slot 1 filled first, names under the tiles, Save,
# X) except the tile list scrolls (16 tribes, 4 per row -> swipe) and a "Match Result" popup can cover the event
# screen. Mapped on xFaktor 2026-11-05. Ends on the main screen. exit 1 -> v_realm_guess.png.
import sys, time
from clash_guess import SLOTS, norm, slot_name, tile
from flow import Stop, find, joined, main, ocr, swipe, tap_wait, wait

BAND = (280, 760)                                           # banner area: a picked tribe's name shows there
FR_BANNER = (600, 400, 1080, 900)


def slot(boxes, rank):
    x0, x1 = SLOTS[rank]
    return ' '.join(t for x, y, w, h, t in boxes if x0 <= x + w // 2 <= x1 and BAND[0] <= y + h // 2 <= BAND[1]
                    and not t[:1].isdigit() and t != 'Guessing')


ROW = 375                                                   # tile row pitch; a swipe moves 2 rows = one page of 8 (Nick 2026-11-05)


def visible(name):
    """Scroll the tile list (top first, then a page at a time) until the tribe shows -> (tap point, boxes)."""
    swipe(540, 800, 540, 800 + 2 * ROW, 800); time.sleep(0.8)   # to the top (slow swipe: no fling)
    for i in range(3):
        boxes = ocr()
        try: return tile(boxes, name), boxes
        except Stop:
            if i == 2: raise
            swipe(540, 800 + 2 * ROW, 540, 800, 800); time.sleep(1)


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
    for rank in (1, 2, 3):                                  # existing guesses -> tap them off in the list, start fresh
        if slot(boxes, rank):
            print(f'{rank}: clearing {slot(boxes, rank)}'); p, _ = visible(slot(boxes, rank)); tap_wait(*p); boxes = ocr()
    if any(slot(boxes, r) for r in (1, 2, 3)): raise Stop(f'slots not cleared: {[slot(boxes, r) for r in (1, 2, 3)]}')
    for rank, want in enumerate(picks, 1):
        p, _ = visible(want); tap_wait(*p); time.sleep(0.8); boxes = ocr()
        have = slot(boxes, rank)
        if norm(want) not in norm(have): raise Stop(f'slot {rank} shows {have!r} after tapping {want!r}; band: {[t for x, y, w, h, t in boxes if BAND[0] <= y + h // 2 <= BAND[1]]}')
        print(f'{rank}: {have}')
    tap_wait(540, 1656); time.sleep(1)                      # Save (no toast)
    tap_wait(974, 224); wait(r'^Guess$', 8, (880, 1800, 1080, 1920))   # close the dialog
    tap_wait(96, 1812); time.sleep(1.5)                     # event screen -> main
    print(f'saved: {[*picks]}')


if __name__ == '__main__':
    if len(sys.argv) != 4: sys.exit('usage: realm_guess.py <1st> <2nd> <3rd>')
    main(run, sys.argv[1:])
