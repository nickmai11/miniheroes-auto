#!/usr/bin/env python3
# Tribe Clash -> Treasure (Chieftain's Treasure): spend the keys on chests, floor by floor. Keys only, no gems.
# usage: D=<serial> scripts/clash_treasure.py   (main screen or Tribe Clash screen); also the last step of tc.py.
# 9 chests per floor, counter "keys/cost" at the bottom (Floor 1 = 1 key, Floor 2 = 2). One chest is the Grand Prize
# (Congratulations popup); its slot then becomes a portal to the next floor, taken at once (Nick 2026-11-11: go to the
# next floor as soon as it's found; the floor's unopened chests are lost). Only closed chests are tapped (pixel check):
# an opened one shows an item card instead.
# Stops when keys < cost (never taps a chest then: no buy popups). Ends on the Tribe Clash screen. exit 1 -> v_clash_treasure.png.
import re, time
from flow import Stop, find, grab, joined, main, near, ocr, tap, tap_text, tap_wait, wait

TILES = [(x, y) for y in (830, 1140, 1450) for x in (230, 540, 850)]


def state():
    im = grab(); b = ocr(im)
    k = next(((int(m[1]), int(m[2])) for x, y, w, h, s in b if 1600 < y < 1720 and (m := re.search(r'(\d+)\s*/\s*(\d+)\b', s))), None)
    f = next((int(m[1]) for x, y, w, h, s in b if 470 < y < 570 and (m := re.search(r'Floor\s*(\d+)', s))), None)
    return k, f, b, im


def read():
    """state() polled ~4 s: the reveal hides the counter and a reward toast the floor header (all 8 accounts 11-11)."""
    for _ in range(6):
        k, f, b, im = state()
        if not near(im.getpixel((60, 1000)), (255, 247, 230)):          # dialog dimmed: Grand Prize popup / item card
            tap(540, 60); time.sleep(1.5); continue                     # top edge closes it (Kong card left from round 1)
        if k and f: return k, f, b, im
        time.sleep(0.7)
    raise Stop(f'Treasure counter/floor not readable: {joined(b)[:150]}')


def closed(im, p):
    """Unopened chest: orange lid + dark keyhole (opened = item icon with a green tick, portal = orange swirl)."""
    return near(im.getpixel((p[0], p[1] - 60)), (255, 130, 90), 25) and near(im.getpixel((p[0], p[1] - 20)), (82, 28, 8), 25)


def after_tap(k):
    """Poll ~5 s for what the tap did: 'opened' / 'prize' / None."""
    for _ in range(8):
        time.sleep(0.7); k2, _, b, _ = state()
        if re.search(r'Congratulation|Tap anywhere', joined(b)): return 'prize', b
        if k2 and k2[0] < k[0]: return 'opened', b
    return None, b


def portal_tile(b):
    """The opened Grand Prize slot (a portal) carries a "Grand Prize" label just above its tile."""
    g = find(b, r'Grand Prize', (0, 650, 1080, 1550))
    return min(TILES, key=lambda p: abs(p[0] - g[0]) + abs(p[1] - 80 - g[1])) if g else None


def floor_pass():
    """Open closed chests until the Grand Prize; then take its portal at once - the rest of the floor is left
    (Nick 2026-11-11). Returns False when keys ran out."""
    k, f, b, im = read()
    tapped = set()
    while not (portal := portal_tile(b)):
        todo = [p for p in TILES if p not in tapped and closed(im, p)]
        if not todo: raise Stop(f'floor {f}: no closed chest and no portal')
        if k[0] < k[1]: print(f'floor {f}: keys {k[0]}/{k[1]} - out of keys'); return False
        p = todo[0]; tapped.add(p); i = TILES.index(p) + 1
        tap(*p); what, b = after_tap(k)
        if what == 'prize': print(f'floor {f} chest {i}: GRAND PRIZE')                  # read() closes the popup
        elif what == 'opened': print(f'floor {f} chest {i}: opened')
        else: raise Stop(f'floor {f} chest {i}: tap did nothing ({joined(b)[:120]})')
        k, f2, b, im = read()
        if f2 != f: raise Stop(f'after chest {i}: floor {f} -> {f2}')
    for _ in range(2):                                                                     # 2 tries (Dino 11-11: 1st tap hit a popup)
        tap(*portal); time.sleep(1.5); b = ocr()
        if 'Proceed to Next Floor' in joined(b):
            tap(320, 1340); time.sleep(0.5); tap_wait(540, 1160)                          # tick "Do not remind me today", Confirm
        for _ in range(6):
            time.sleep(0.7); _, f2, _, _ = state()
            if f2 and f2 != f: print(f'-> floor {f2}'); return True
    raise Stop(f'floor {f}: portal did not lead to the next floor')


def run():
    b = ocr()
    if not find(b, r'Chieftain'):
        if not find(b, r'^Guess$', (900, 1800, 1080, 1920)):
            tap_text(r'Tribe Clash', (680, 560, 1080, 680), b)                            # main-screen banner
            wait(r'^Guess$', 10, (900, 1800, 1080, 1920))
        tap_wait(980, 1300); wait(r'Chieftain', 8)                                         # Treasure
    while floor_pass(): pass
    k, f, _, _ = read()
    tap_wait(972, 248); wait(r'^Guess$', 8, (900, 1800, 1080, 1920))                       # close -> Tribe Clash screen
    print(f'treasure done: floor {f}, keys {k[0]}/{k[1]}' if k else f'treasure done: floor {f}')


if __name__ == '__main__':
    main(run)
