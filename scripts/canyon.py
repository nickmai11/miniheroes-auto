#!/usr/bin/env python3
# Canyon Clash: move to an EMPTY platform (free, no attempt) by the day's rule. Canyon map must be open.
# usage: D=<serial> scripts/canyon.py <account>    (ui-routine "Canyon Clash"; Nick 2026-10-28: script, not a helper)
#   Mon-Fri: first empty purple (Silver) platform among the top silver rows.
#   Sat-Sun: empty Gold first, else empty purple.     canyon_clash: highest_free -> topmost empty platform of any kind.
# Empty = a platform disc with no name label under it. Every pick is confirmed by the popup text "occupy the empty"
# before Occupy; anything else ("About to challenge <name>'s ...") -> Cancel. Never attacks: no empty spot -> exit 2.
# exit 0 = moved, 2 = no empty platform (helper may beat a Sentinel; never a player), 1 = unexpected screen.
import datetime, fcntl, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flow import Stop, find, main, near, ocr, swipe, tap_text, wait
from tap import grab, tap as tap_wait

PURPLE, GOLD = (203, 157, 255), (252, 170, 110)   # empty disc colours (Tiger 2026-10-28)


def empties(im, boxes, colour):
    """Centres of platform discs of `colour` with no OCR text (name / CP label) 40-200 px below them."""
    cells = {}
    for y in range(330, 1800, 6):
        for x in range(60, 1020, 6):
            if near(im.getpixel((x, y)), colour, 25): cells.setdefault((x // 150, y // 150), []).append((x, y))
    blobs = []
    for pts in cells.values():
        if len(pts) < 40: continue
        cx, cy = sum(p[0] for p in pts) // len(pts), sum(p[1] for p in pts) // len(pts)
        if any(abs(b[0] - cx) < 140 and abs(b[1] - cy) < 140 for b in blobs): continue
        blobs.append((cx, cy))
    labelled = lambda cx, cy: any(abs(x + w // 2 - cx) < 130 and 30 < y - cy < 220 for x, y, w, h, t in boxes)
    return sorted((b for b in blobs if not labelled(*b)), key=lambda b: (b[1], b[0]))


def settled():
    """Grab once the map stopped scrolling (inertia: taps during it miss — ui-routine Canyon)."""
    a = grab()
    for _ in range(8):
        time.sleep(0.4); b = grab()
        if sum(1 for x in range(100, 1000, 50) for y in range(400, 1800, 50) if not near(a.getpixel((x, y)), b.getpixel((x, y)), 8)) < 5:
            return b
        a = b
    return a


def try_occupy(x, y):
    # ponytail: one global lock around tap -> popup -> Occupy only; accounts scan in parallel. Our accounts share the
    # map and raced for one spot (2026-10-29); a whole-run lock queued them for minutes (2026-10-31). Freed on return.
    lock = open('/tmp/miniheroes-canyon.lock', 'w'); fcntl.flock(lock, fcntl.LOCK_EX)
    tap_wait(x, y)
    for _ in range(6):                                  # popup slides in
        time.sleep(0.5); boxes = ocr(); t = ' '.join(b[4] for b in boxes)
        if find(boxes, r'^Cancel$'): break
    else: return False                                  # no popup: the tap missed, nothing to close
    if re.search(r'occupy the empty', t, re.I) and find(boxes, r'^Occupy$'):
        tap_text(r'^Occupy$', boxes=boxes)
        seen = False                                    # old spot's gains: "Resource" Confirm popup and/or a
        for i in range(24):                             # "Congratulations" one (Tap anywhere to close); either ate the
            time.sleep(0.5); b2 = ocr()                 # Rewards tap -> FAIL -> retry re-occupied (7 accounts 11-05)
            if find(b2, r'^Confirm$'): tap_text(r'^Confirm$', boxes=b2); seen = True; continue
            if find(b2, r'Congratulations|Tap anywhere'): tap_wait(540, 1300); seen = True; continue
            if seen or i >= 10: break                   # popups gone (or none within 5 s: no old spot)
        return True
    tap_text(r'^Cancel$', boxes=boxes)
    return False


def run(account):
    cfg = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'accounts', account + '.yaml')).read()
    head = wait(r'Attempts', 10)
    highest = bool(re.search(r'canyon_clash:\s*highest_free', cfg))
    # highest_free keeps a spot that's higher than any empty one: it moved Tiger Glory -> Gold (2026-11-03)
    cur = next((t for t in ('Glory', 'Gold', 'Silver') if find(head, rf'^{t} Battlefield', (0, 0, 1080, 330))), '')
    tier = {'Glory': 3, 'Gold': 2, 'Silver': 1}.get(cur, 0)
    weekend = datetime.datetime.now().weekday() >= 5
    for _ in range(6): swipe(540, 600, 540, 1500, 300)                # to the top of the map
    time.sleep(1)
    colours = [GOLD, PURPLE] if highest or weekend else [PURPLE]
    if highest: colours = [c for c in colours if {GOLD: 2, PURPLE: 1}[c] >= tier]
    if not colours: print(f'keeping the current {cur} spot: higher than any empty one (highest_free)'); return 0
    purple_screens = 0
    for screen in range(12):
        im = settled(); boxes = ocr(im); im.resize((270, 480)).save(f'canyon{screen}.png')   # per-screen record (2026-10-29)
        print(f'screen {screen}: purple discs {len(empties(im, [], PURPLE))}, empty {len(empties(im, boxes, PURPLE))}'
              + ('' if any('Attempts' in b[4] for b in boxes) else ', NOT ON THE MAP'), flush=True)
        for colour in colours:
            for x, y in empties(im, boxes, colour):
                if try_occupy(x, y):
                    print(f'occupied empty {"purple" if colour == PURPLE else "gold"} platform (screen {screen})'); return 0
        if empties(im, [], PURPLE) or any('Silver' in b[4] for b in boxes if b[1] > 330): purple_screens += 1  # not the header
        if purple_screens >= 2 and not highest: break                 # only the top silver rows (~10 spots)
        swipe(540, 1500, 540, 700, 600); time.sleep(1.5)
    print('no empty platform found'); return 2


if __name__ == '__main__':
    main(run, sys.argv[1])
