#!/usr/bin/env python3
# Tribe Clash -> Treasure (Chieftain's Treasure): spend the keys on chests, floor by floor. Keys only, no gems.
# usage: D=<serial> scripts/clash_treasure.py   (main screen or Tribe Clash screen); also the last step of tc.py.
# 9 chests per floor, counter "keys/cost" at the bottom (Floor 1 = 1 key, Floor 2 = 2). One chest is the Grand Prize
# (Congratulations popup); its slot then becomes a portal to the next floor - whose Tip says unclaimed rewards on the
# floor are lost, so every chest is opened before the portal (Kong 2026-11-11). Tapping an opened chest shows an item
# card (top edge closes it; with no popup open that tap closes the whole dialog - so only on a card).
# Stops when keys < cost (never taps a chest then: no buy popups). Ends on the Tribe Clash screen. exit 1 -> v_clash_treasure.png.
import re, time
from flow import Stop, find, joined, main, ocr, tap, tap_text, tap_wait, wait

TILES = [(x, y) for y in (830, 1140, 1450) for x in (230, 540, 850)]


def state():
    b = ocr()
    k = next(((int(m[1]), int(m[2])) for x, y, w, h, s in b if 1600 < y < 1720 and (m := re.search(r'(\d+)\s*/\s*(\d+)\b', s))), None)
    f = next((int(m[1]) for x, y, w, h, s in b if 470 < y < 570 and (m := re.search(r'Floor\s*(\d+)', s))), None)
    return k, f, b


def after_tap(k, f):
    """Poll ~5 s for what the tap did: 'opened' / 'prize' / 'portal' / 'card' / 'floor' / None."""
    for _ in range(8):
        time.sleep(0.7); k2, f2, b = state(); t = joined(b)
        if re.search(r'Congratulation|Tap anywhere', t): return 'prize', b
        if k2 and k and k2[0] < k[0]: return 'opened', b
        if find(b, r'[A-Za-z]{4,} [A-Za-z]{3,}', (330, 900, 960, 1100)): return 'card', b   # item description lines
    return None, b


def portal_tile():
    """The opened Grand Prize slot (a portal) carries a "Grand Prize" label just above its tile."""
    g = find(ocr(), r'Grand Prize', (0, 650, 1080, 1550))
    return min(TILES, key=lambda p: abs(p[0] - g[0]) + abs(p[1] - 80 - g[1])) if g else None


def floor_pass():
    """Open every chest on this floor; then take the portal. Returns False when keys ran out."""
    k, f, _ = state()
    if not k or not f: raise Stop('Treasure counter/floor not readable')
    portal = None
    for i, p in enumerate(TILES):
        if portal is None: portal = portal_tile()
        if p == portal: continue                                    # the portal last: it drops what is still closed
        if k[0] < k[1]: print(f'floor {f}: keys {k[0]}/{k[1]} - out of keys'); return False
        tap(*p); what, b = after_tap(k, f)
        if what == 'prize': tap(540, 60); time.sleep(2); print(f'floor {f} chest {i + 1}: GRAND PRIZE')
        elif what == 'opened': print(f'floor {f} chest {i + 1}: opened')
        elif what == 'card': tap(540, 60); time.sleep(1.2)          # already opened
        else: raise Stop(f'floor {f} chest {i + 1}: tap did nothing ({joined(b)[:120]})')
        k2, f2, _ = state()
        if not k2 or f2 != f: raise Stop(f'after chest {i + 1}: counter {k2}, floor {f} -> {f2}')
        k = k2
    portal = portal or portal_tile()
    if not portal: print(f'floor {f}: all opened, no portal found'); return False
    tap(*portal); time.sleep(1.5); b = ocr()
    if 'Proceed to Next Floor' in joined(b):
        tap(320, 1340); time.sleep(0.5); tap_wait(540, 1160)                              # tick "Do not remind me today", Confirm
    for _ in range(6):
        time.sleep(0.7); _, f2, _ = state()
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
    k, f, _ = state()
    tap_wait(972, 248); wait(r'^Guess$', 8, (900, 1800, 1080, 1920))                       # close -> Tribe Clash screen
    print(f'treasure done: floor {f}, keys {k[0]}/{k[1]}' if k else f'treasure done: floor {f}')


if __name__ == '__main__':
    main(run)
