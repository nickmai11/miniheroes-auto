#!/usr/bin/env python3
"""Golden Woods -> King's Treasury (Nick 2026-11-09): spend the Treasury Keys flipping cards (1 key each) until the
level's Grand Prize shows, then GO to the next level, until the keys run out. Prize pick (before each level's free
Shuffle Cards): the newest unlocked prize (Level 3 / 5 / 7 tiles) up to Level 7; from Level 7 on always the Level 7
prize (Level 10 / 15 ignored): picked on entering Level 3, 5 and 7, kept on the others.
Cards are flipped in random order (Nick 2026-11-09; the game says every card has an equal chance).
usage: D=<serial> scripts/treasury.py <account> [--max-keys N]   from the main screen (or already on King's Treasury)."""
import random, re, sys, time
from flow import Stop, find, grab, joined, main, near, ocr, tap_wait, wait

XS, YS = (414, 596, 776, 958), (910, 1092, 1274, 1454)          # card grid centres
# prize picker: tiles in a fixed order, 4 per row (x below), rows 224 px apart; locked ones carry a "Level N" label
# ~110 px under the tile, gone once unlocked. The list scrolls (Level 5 entry showed it from row 2, Bino 2026-11-09)
# -> place the target relative to any visible label.
ORDER = {3: 3, 5: 4, 7: 5, 10: 6, 15: 7, 20: 8}               # unlock level -> tile index (0-2: the free starters)
COLS = (228, 436, 646, 856)
TAN = (206, 158, 99)                                            # unflipped card, 60 px up-left of its centre


def log(s): print(s, flush=True)


def open_treasury():
    b = ocr()
    if find(b, r"King.?s Treasury") and find(b, r'^Level \d'): return
    from daily import hub_tabs
    tap_wait(896, 340); wait(r'Match|Weekly', 10, (0, 1760, 1080, 1920)); time.sleep(1.2)
    x = hub_tabs().get('golden_woods')
    if not x: raise Stop('no Golden Woods tab in the event hub')
    tap_wait(x, 1840); tap_wait(165, 300); wait(r'^Level \d', 8)


def state():
    for _ in range(4):                                           # a reward toast can cover the "Level N" label
        b = ocr()
        if find(b, r'^Level \d+$'): break
        time.sleep(0.8)
    lv = next((int(m.group(1)) for *_, t in b if (m := re.match(r'^Level (\d+)$', t.strip()))), None)
    keys = find(b, r'^\d+$', (290, 30, 500, 110))
    keys = next((int(t) for x, y, w, h, t in b if (x + w // 2, y + h // 2) == keys), None) if keys else None
    return b, lv, keys


def pick_prize(lv):
    if lv not in (3, 5, 7): return                               # the pick sticks across levels (L2 kept L1's)
    tap_wait(154, 1320); time.sleep(0.6); b = wait(r'select a prize', 6)
    anchor = next(((n, find(b, rf'^Level {n}$', (0, 900, 1080, 1420))) for n in ORDER if n > lv
                   and find(b, rf'^Level {n}$', (0, 900, 1080, 1420))), None)
    if not anchor: raise Stop(f'prize picker: no "Level N" label to place the Level {lv} tile; {joined(b)[:200]}')
    (n, (ax, ay)), i, j = anchor, ORDER[lv], ORDER[anchor[0]]
    x, y = COLS[i % 4], ay - 110 + 224 * (i // 4 - j // 4)
    if not 900 < y < 1400: raise Stop(f'Level {lv} tile at y={y}, outside the picker list')
    tap_wait(x, y); time.sleep(0.5)
    if not near(grab().getpixel((x - 76, y)), (0, 231, 107), 40):     # green frame on the tile's left edge = selected
        raise Stop(f'Level {lv} prize not selected at {x},{y} (locked or used up?)')
    tap_wait(540, 1496)                                          # Save
    log(f'  level {lv}: prize = Level {lv} tile')


def milestones():
    """Point bar (1 point per flip; 50/100/150/200/250): claim each icon with a red dot (~30 px right, 40 up). Free."""
    for x in (310, 484, 656, 830, 1002):
        if near(grab().getpixel((x + 30, 450)), (255, 0, 74), 40):
            tap_wait(x, 490); b = wait(r'Tap anywhere', 4); tap_wait(*find(b, r'Tap anywhere')); log(f'  milestone {x} claimed')


def run(acct, max_keys=999):
    open_treasury(); used = lv_flips = 0
    while True:
        b, lv, keys = state()
        if lv is None: raise Stop(f'level unreadable: {joined(b)[:200]}')
        # ponytail: keys OCR drops/misreads a single digit (9 -> 6 or nothing, Bino 2026-11-09) -> only "0" stops;
        # an unreadable count just flips, and the out-of-keys screen after a flip ends the run
        if find(b, r'^Shuffle Cards$'):
            pick_prize(lv); tap_wait(540, 1616); time.sleep(1.5); log(f'level {lv}: shuffled, keys {keys}'); continue
        if find(b, r'Next floor available') or find(b, r'^GO$', (0, 1340, 320, 1480)):
            tap_wait(154, 1408); time.sleep(1)
            b = ocr()
            if find(b, r'proceed to the next level'):            # tick "Do not remind me today" (persists today), Confirm
                tap_wait(320, 1343); b = ocr()
                if find(b, r'proceed to the next level'): tap_wait(538, 1162)
            wait(rf'^Level {lv + 1}$', 8); log(f'level {lv} -> {lv + 1}'); lv_flips = 0; continue
        if keys == 0 or used >= max_keys:
            milestones(); log(f'DONE level {lv}, keys {keys}, flips {used}'); return
        im = grab()
        cards = [(x, y) for y in YS for x in XS if near(im.getpixel((x - 60, y - 60)), TAN, 20)]
        if not cards: raise Stop(f'level {lv}: no unflipped card but no Next floor either')
        c = random.choice(cards); tap_wait(*c); time.sleep(0.6)
        b = ocr()
        # keys OCR misses a lone "0" -> the flip answers with a toast over the still-flippable board (xFaktor/Chien Than
        # 2026-11-09 kept tapping it): the toast, or the card still face down, = out of keys
        if find(b, r'Insufficient') or near(grab().getpixel((c[0] - 60, c[1] - 60)), TAN, 20):
            milestones(); log(f'DONE level {lv}, keys 0 (flip refused), flips {used}'); return
        used += 1; lv_flips += 1
        if find(b, r'obtained the Level Prize'):
            tap_wait(*(find(b, r'Tap anywhere') or (540, 1208)))
            log(f'level {lv}: Grand Prize after {lv_flips} flips')
        elif not find(b, r'Tap to flip'): raise Stop(f'after a flip: {joined(b)[:200]}')


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0].startswith('-'): sys.exit(__doc__)
    main(run, a[0], int(a[a.index('--max-keys') + 1]) if '--max-keys' in a else 999)
