#!/usr/bin/env python3
# Tribe Clash Guessing: pick the 1st / 2nd / 3rd tribe and Save. Free, no gems.
# usage: D=<serial> scripts/clash_guess.py "dragon slayers" potato "purple gang"   (main screen or Tribe Clash screen)
# Names match case/space/emoji-insensitively against the tile labels. Picking a tribe fills the selected slot
# (1 first) and moves the selection 1 -> 2 -> 3 (Cmajor 2026-10-29). Existing guesses are cleared first
# (tap the picked tile in the list), then all 3
# picked fresh (Nick 2026-10-29). Save shows no toast; not re-verified (Nick 2026-10-29: no double check).
# Ends on the Tribe Clash screen, dialog closed. Tested on Cmajor 2026-10-29. exit 1 -> v_clash_guess.png.
import re, sys, time
from flow import Stop, find, joined, main, ocr, tap_text, tap_wait, wait

SLOTS = {1: (390, 690), 2: (0, 390), 3: (690, 1080)}     # slot x ranges; names show at y~595 under each banner
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())


def slot_name(boxes, rank):
    x0, x1 = SLOTS[rank]
    return ' '.join(t for x, y, w, h, t in boxes if x0 <= x + w // 2 <= x1 and 540 <= y + h // 2 <= 660
                    and not re.search(r'\d+M$', t))


def run(picks):
    boxes = ocr()
    if find(boxes, r'Please select a tribe'): return pick(boxes, picks)   # dialog already open (Guess shows under it)
    if not find(boxes, r'^Guess$', (900, 1800, 1080, 1920)):
        tap_text(r'Tribe Clash', (680, 560, 1080, 680), boxes)   # main-screen banner
        boxes = wait(r'^Guess$', 10, (900, 1800, 1080, 1920))
    pick(open_guess(boxes), picks)


def open_guess(boxes):
    """Tap the dice above the Guess label; a 2nd try if ignored (too early after the screen opened: Dino/Dminor/Tiger)."""
    g = find(boxes, r'^Guess$', (900, 1800, 1080, 1920))
    for i in (1, 2):
        tap_wait(g[0], g[1] - 50)
        try: return wait(r'Please select a tribe', 4)
        except Stop:
            if i == 2: raise


def tile(boxes, name):
    """The list tile's icon (~100 px above its name). Tapping a picked tile removes it from its slot."""
    p = next(((x + w // 2, y + h // 2 - 100) for x, y, w, h, t in boxes
              if 800 <= y <= 1560 and norm(name) and (norm(name) in norm(t) or norm(t) in norm(name) and len(norm(t)) > 3)), None)
    if not p: raise Stop(f'no tribe {name!r} in the list: {joined(boxes)[:300]}')
    return p


def pick(boxes, picks):
    for rank in (1, 2, 3):                 # Nick: existing guesses -> tap them off, start fresh (tapping the slot does nothing)
        if slot_name(boxes, rank):
            print(f'{rank}: clearing {slot_name(boxes, rank)}'); tap_wait(*tile(boxes, slot_name(boxes, rank))); boxes = ocr()
    if any(slot_name(boxes, r) for r in (1, 2, 3)): raise Stop(f'slots not cleared: {[slot_name(boxes, r) for r in (1, 2, 3)]}')
    for rank, want in enumerate(picks, 1):
        tap_wait(*tile(boxes, want))
        boxes = ocr()
        have = slot_name(boxes, rank)
        if norm(want) not in norm(have): raise Stop(f'slot {rank} shows {have!r} after tapping {want!r}')
        print(f'{rank}: {have}')
    tap_wait(540, 1656)                                       # Save (OCR misses it once it turns green)
    time.sleep(1); tap_wait(972, 222)                         # close (no toast; no reopen check, Nick 2026-10-29)
    wait(r'^Guess$', 8, (900, 1800, 1080, 1920))
    print(f'saved: {[*picks]}')

if __name__ == '__main__':
    if len(sys.argv) != 4: sys.exit(__doc__ or 'usage: clash_guess.py <1st> <2nd> <3rd>')
    main(run, sys.argv[1:])
