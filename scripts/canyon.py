#!/usr/bin/env python3
# Canyon Clash: move to an EMPTY platform (free, no attempt) by the day's rule. Canyon map must be open.
# usage: D=<serial> scripts/canyon.py <account>    (ui-routine "Canyon Clash"; Nick 2026-10-28: script, not a helper)
#   Mon-Thu: first empty purple (Silver) platform among the top silver rows.
#   Fri-Sun: empty Gold first, else empty purple (Fri since Nick 2026-11-08, was Sat).
#   canyon_clash: highest (Nick 2026-11-24: script, not a helper): any day, the topmost empty Gold / purple platform,
#     walking down past blue (tribemate) and green (own) name plates; a plate of any other colour above it -> exit 2.
#   Purple enough (Nick 2026-11-21; not on a highest account - Nick 2026-11-25): points + 9/min x minutes to season end x 22/24 >= 80k -> purple only.
# Empty = a platform disc with no name label under it. Every pick is confirmed by the popup text "occupy the empty"
# before Occupy; anything else ("About to challenge <name>'s ...") -> Cancel. Never attacks: no empty spot -> exit 2.
# exit 0 = moved, 2 = no empty platform (helper attacks: a Sentinel, else a non-tribe player), 1 = unexpected screen.
import datetime, fcntl, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flow import Stop, find, main, near, ocr, swipe, tap_text, wait
from tap import grab, tap as tap_wait

PURPLE, GOLD = (203, 157, 255), (252, 170, 110)   # empty disc colours (Tiger 2026-10-28)
TARGET, PURPLE_RATE = 80000, 9                    # points-reward top tier; purple spot points/min (Nick 2026-11-21)
HELD = 22 / 24                                    # share of the time a spot is actually held: 8 h occupations, runs between (Nick 2026-11-21: ~22 h a day)


def season_left(now):
    """Minutes from `now` (aware) to the season end, Sunday 23:00 UTC (= Monday 06:00 local)."""
    now = now.astimezone(datetime.timezone.utc)
    end = (now + datetime.timedelta(days=(6 - now.weekday()) % 7)).replace(hour=23, minute=0, second=0, microsecond=0)
    if end <= now: end += datetime.timedelta(days=7)
    return int((end - now).total_seconds() // 60)


def purple_enough(points, minutes):
    """Staying on a purple (9/m) spot until the season ends reaches 80k -> no Gold/Glory (Nick 2026-11-21: leave them)."""
    return points is not None and points + projected(minutes) >= TARGET


def projected(minutes):
    return int(PURPLE_RATE * minutes * HELD)


def read_points():
    """Map -> Rewards panel (88,745) -> its points number -> close (972,240) -> map. None = unreadable."""
    tap_wait(88, 745); boxes = wait(r'Points Reward', 10)
    pts = next((int(t) for x, y, w, h, t in boxes if 240 <= x + w // 2 <= 420 and re.fullmatch(r'\d{3,6}', t.strip())), None)
    tap_wait(972, 240); wait(r'Attempts', 10)
    return pts


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


def plate(im, cx, cy):
    """Name plate above the CP label centred (cx, cy): 'blue' = tribemate, 'green' = this account, None = neither
    (Kratos map 2026-11-24: blue 58,125,195 - 39,84,132 in the shaded bottom rows - green 0,150,16)."""
    px = [im.getpixel((x, y))[:3] for y in range(cy - 84, cy - 27, 6) for x in range(max(cx - 72, 0), min(cx + 73, im.width), 8)]
    blue = sum(1 for r, g, b in px if b - r > 50 and b > g)
    green = sum(1 for r, g, b in px if g - r > 80 and g - b > 80)
    return 'green' if green * 5 > len(px) else 'blue' if blue * 5 > len(px) else None


def foes(im, boxes):
    """(x, y) of the platforms held by neither a tribemate nor this account: a CP label ('2960k') under a plate that is
    not blue / green. y ~ the platform (136 px above its CP label)."""
    cps = [(x + w // 2, y + h // 2) for x, y, w, h, t in boxes if y > 330 and re.search(r'\d{3,5}k$', t.strip(), re.I)]
    return [(cx, cy - 136) for cx, cy in cps if plate(im, cx, cy) is None]


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
    wait(r'Attempts', 10)
    highest = bool(re.search(r'canyon_clash:\s*highest\b', cfg))
    pts, left = read_points(), season_left(datetime.datetime.now().astimezone())
    enough = not highest and purple_enough(pts, left)   # highest accounts keep the highest rule (Nick 2026-11-25)
    print(f'points {pts}, {left} min to season end -> {"purple enough" if enough else "highest: purple rule off" if highest else "purple not enough"}'
          + (f' ({pts + projected(left)} at {PURPLE_RATE}/m, 22 h a day)' if pts is not None else ''), flush=True)
    # highest: the topmost spot that isn't a tribemate's - empty, Sentinel or player (Nick 2026-11-19). The script takes
    # the topmost EMPTY one (Nick 2026-11-24: plates are blue or green, skip them); anything else above it = helper attacks.
    # ponytail: empty Kings / Glory discs aren't detected (colours never seen) - add them to `colours` once one shows.
    weekend = datetime.datetime.now().weekday() >= 4   # Fri-Sun (Nick 2026-11-08: top spot from Friday, not Saturday)
    for _ in range(6): swipe(540, 600, 540, 1500, 300)                # to the top of the map
    time.sleep(1)
    colours = [GOLD, PURPLE] if (weekend and not enough) or highest else [PURPLE]
    purple_screens = 0
    for screen in range(12):
        im = settled(); boxes = ocr(im); im.resize((270, 480)).save(f'canyon{screen}.png')   # per-screen record (2026-10-29)
        print(f'screen {screen}: purple discs {len(empties(im, [], PURPLE))}, empty {len(empties(im, boxes, PURPLE))}'
              + ('' if any('Attempts' in b[4] for b in boxes) else ', NOT ON THE MAP'), flush=True)
        spots = [(x, y, colour) for colour in colours for x, y in empties(im, boxes, colour)]
        if highest:
            spots.sort(key=lambda s: s[1])                # top-down; a foe in the first empty one's row doesn't count
            above = [f for f in foes(im, boxes) if not spots or f[1] < spots[0][1] - 150]
            if above: print(f'highest: non-tribemate spot at {above[0]} above the first empty one (screen {screen}) -> helper attacks'); return 2
        for x, y, colour in spots:
            if try_occupy(x, y):
                print(f'occupied empty {"purple" if colour == PURPLE else "gold"} platform (screen {screen})'); return 0
        if empties(im, [], PURPLE) or any('Silver' in b[4] for b in boxes if b[1] > 330): purple_screens += 1  # not the header
        if purple_screens >= 2: break                 # only the top silver rows (~10 spots)
        swipe(540, 1500, 540, 700, 600); time.sleep(1.5)
    print('no empty platform found' + (' (purple enough)' if enough else '')); return 2


if __name__ == '__main__':
    main(run, sys.argv[1])
