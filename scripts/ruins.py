#!/usr/bin/env python3
"""Adventure -> Ancient Ruins (Nick 2026-11-26: finish the floors asap). Explores the ruin in the crystal ball: on each
floor the shortest tile path to the door / Ultimate Chest (its faint icon shows from the start), re-read after every tap
(roadblocks = not walkable -> the path goes round), revealed rewards tapped once (free), Exit at the Ultimate Chest. Then
Search for the next ruin - free, or diamonds up to SEARCH_CAP - and on, until the stamina is out (the ruin keeps its
state). Never the "Stamina depleted" purchase. Cards (Nick 2026-11-26: use them): Fireball burns the roadblock that
shortens the way (or walls it in), Lightning removes the monster in the way; no Lightning -> it is fought (lineup as it
stands, 2 stamina) when going round costs more. A lost fight, no way through, or an unknown dialog = exit 1 ->
v_ruins.png, by hand.
usage: D=<serial> scripts/ruins.py [account]   from the main screen. Last line = the result."""
import re, sys, time
from collections import deque
from flow import Stop, adventure, find, grab, is_main, joined, main, near, ocr, tap_wait, wait

SEARCH_CAP = 50                         # top diamond price of one Search (Nick 2026-11-26); the stamina purchase: never
PAID_WALKED = False                     # a priced Search hasn't been walked by hand yet (CLAUDE.md "Paid buys") -> not tapped until it has
DARK, LIGHT = 'dark', 'light'           # unexplored / explorable (next to an explored tile)
HOLE, OUT = (41, 45, 41), (49, 45, 41)  # explored and empty (every theme); outside a small ruin's rows
CROSS, WOOD = (165, 53, 49), (124, 84, 44)   # the red X on a tile a monster blocks; a roadblock's spikes
CARDS = {'Fireball': 540, 'Lightning': 706}   # card x (y 1780); its count sits at the card's bottom right
BUY = r'diamonds to purchase'           # the stamina offer ("Stamina depleted" on a floor, "Tip" on a monster's lineup): X, never Confirm
ROWS = 11                               # row 0 = the start's row (y 1600), 126.6 px per row up; Small Ruin uses rows 0-8
# ponytail: one fixed grid of 11 rows (Cmajor's Small Ruin used 9, Tiger's Frozen Cliff all 11). A floor
# where this grid doesn't fit stops with exit 1 (no icon / no path); measure that grid then.


def log(s): print(s, flush=True)


def cols(r): return 5 if r % 2 == 0 else 6


def centre(r, k): return (210 if r % 2 == 0 else 130) + 170 * k, round(1600 - 126.6 * r)


def neighbours(r, k):
    """Odd rows sit 80 px left of the even ones: an even tile's upper / lower neighbours are k and k+1, an odd one's k-1 and k."""
    side = (k, k + 1) if r % 2 == 0 else (k - 1, k)
    for rr, kk in [(r, k - 1), (r, k + 1)] + [(r + d, s) for d in (-1, 1) for s in side]:
        if 0 <= rr < ROWS and 0 <= kk < cols(rr): yield rr, kk


def tone(c):
    """Brightness of a tile edge that shows theme ground (unexplored or explorable), None for explored ground, the
    outside, wood and grey sprites. Measured 2026-11-26, unexplored / explorable: Clearwater (41,69,41) / (107,169,99),
    Frozen Cliff (25,49,74) / (66,116,178), Amethyst Cavern (16,24,41) / (49,61,99), Divine Battleground (33,32,41) /
    (90,77,107) - the last two read as nothing / unexplored with the first fixed thresholds (Kong, Tiger, Kratos, Dminor)."""
    v, d = max(c), max(c) - min(c)
    if v < 30 or near(c, HOLE, 6) or near(c, OUT, 6) or near(c, WOOD, 25): return None
    return v if d >= 20 or (v < 50 and d >= 8) else None


def kind(c, cut=122):
    v = tone(c)
    return None if v is None else LIGHT if v >= cut else DARK


def sides(im, r, k):
    x, y = centre(r, k)
    return im.getpixel((x - 60, y)), im.getpixel((x + 60, y))   # the tile's edges: icons, light beams and sprites sit mid-tile


def edge(im, r, k):
    """The tile's ground brightness when both its edges show the same theme ground, else None (explored, outside,
    something standing across it)."""
    a, b = sides(im, r, k)
    return tone(a) if near(a, b, 25) else None


def wood(im, r, k):
    """Wood-coloured dots on the tile: a roadblock 39-44 of 81, a gold sack 24-29, the start pedestal 33 (Kong II,
    Kratos, Dminor 2026-11-26)."""
    x, y = centre(r, k)
    return sum(near(im.getpixel((x + dx, y + dy)), WOOD, 30) for dx in range(-40, 41, 10) for dy in range(-40, 41, 10))


def read(im):
    """({(r, k): DARK | LIGHT} = tiles still to explore, the target = the tile with the door / chest icon,
    the red-X tiles a monster blocks, the roadblocks)."""
    tones = {(r, k): v for r in range(ROWS) for k in range(cols(r)) if (v := edge(im, r, k))}
    # ponytail: two brightness regimes instead of a colour per theme - a bright theme's explorable tiles are >= 140 and
    # its unexplored ones < 115, a dark theme's 99-107 and 41. A new theme outside both -> no icon / no path, exit 1.
    cut = 122 if any(v >= 140 for v in tones.values()) else 70
    grid = {t: LIGHT if v >= cut else DARK for t, v in tones.items()}
    crossed = {t for t in grid if near(im.getpixel(centre(*t)), CROSS, 30)}
    for t in crossed: del grid[t]
    blocks = {(r, k) for r in range(ROWS) for k in range(cols(r)) if (r, k) not in tones and (r, k) != (0, 2) and wood(im, r, k) >= 36}
    def marks(t):
        (x, y), a = centre(*t), sides(im, *t)[0]
        return sum(not near(im.getpixel((x + dx, y + dy)), a, 20) for dx in range(-48, 49, 6) for dy in range(-48, 49, 6))
    # the icon tile = far more off-colour dots than its kind's usual texture (forest: 0-2, chest icon 28, door 58+; ice's
    # explorable tiles ~27, its door 85). Row 0 left out: the Exploration Assistant's hat covers its right tile.
    m = {t: marks(t) for t in grid if t[0]}
    usual = {b: sorted(v for t, v in m.items() if grid[t] == b)[sum(grid[t] == b for t in m) // 2] for b in set(grid[t] for t in m)}
    best = max(m, key=lambda t: m[t] - usual[grid[t]], default=None)
    icon = best if best and m[best] - usual[grid[best]] >= 15 else None
    if not icon:   # no faint icon: the door is lit already (a floor explored by hand: Kong II, Boudior 2026-11-26)
        icon = next(((r, k) for r in range(1, ROWS) for k in range(cols(r)) if (r, k) not in tones and lit_door(im, r, k)), None)
    return grid, icon, crossed, blocks


def lit_door(im, r, k):
    """A lit door = dark stone gate with a yellow arrow up (the way in, row 0, has a blue arrow down): 12 yellow dots in
    the tile on both doors seen, the arrow's 4 centre dots yellow, stone left and right of it."""
    x, y = centre(r, k); px = lambda dx, dy: im.getpixel((x + dx, y + dy))
    yellow = lambda p: p[0] > 220 and p[1] > 160 and p[2] < 150
    stone = lambda p: max(p) < 95 and max(p) - min(p) < 25
    n = sum(yellow(px(dx, dy)) for dx in range(-50, 51, 10) for dy in range(-60, 41, 10))
    return (9 <= n <= 15 and all(yellow(px(*d)) for d in ((0, 0), (0, 10), (0, -10), (10, -10)))
            and all(stone(px(*d)) for d in ((-40, 0), (40, 0), (-40, -30), (40, -30), (0, -40))))


def monster(im, grid, crossed, target, blocks=()):
    """The monster in the way = the thing standing next to the crossed tile nearest the target."""
    # ponytail: "a non-empty explored tile beside an X" also fits a reward or roadblock next to a monster's X; the one
    # with the most X neighbours wins, a wrong pick is a wasted tap and the 4-idle-taps Stop ends it.
    seen, q = {target}, deque([target])
    while q:
        t = q.popleft()
        if t in crossed:
            c = [n for n in neighbours(*t) if n not in grid and n not in crossed and n not in blocks and n != (0, 2)
                 and not near(im.getpixel(centre(*n)), HOLE, 14) and tone(sides(im, *n)[0]) is None and not near(sides(im, *n)[0], (16, 24, 25), 40)]
            if c: return max(c, key=lambda n: sum(m in crossed for m in neighbours(*n)))
        for n in neighbours(*t):
            if (n in grid or n in crossed) and n not in seen: seen.add(n); q.append(n)


def path(grid, target, burnt=()):
    """(tiles still to explore to stand on the target = the stamina it costs, the explorable tile to tap first); (None,
    None) = walled in. BFS out from the target through unexplored tiles to the first explorable one; the tiles next to
    `burnt` (a roadblock about to be removed) count as explorable."""
    opened = {n for b in burnt for n in neighbours(*b)}
    seen, q = {target}, deque([(target, 1)])
    while q:
        t, d = q.popleft()
        if grid[t] == LIGHT or t in opened: return d, t
        for n in neighbours(*t):
            if n in grid and n not in seen: seen.add(n); q.append((n, d + 1))
    return None, None


def step(grid, target): return path(grid, target)[1]


def cards(im):
    """{card: count}: the digit at each card's bottom right, 4x crop (15 of 16 saved counts read; a 0 reads as nothing).
    Unreadable = 0: a card is only tapped with a count >= 1 read (a card at 0 keeps its colour; its tap was never tried)."""
    out = {}
    for name, x in CARDS.items():
        c = im.crop((x - 30, 1790, x + 90, 1890)); t = ''.join(t for *_, t in ocr(c.resize((c.width * 4, c.height * 4)))).strip()
        out[name] = int(t) if re.fullmatch(r'[1-9]', t) else 0
    return out


def coverable(t):
    """The selected card opens enlarged over the bottom centre (x 380-712, y 1440+): a tile under it can't be tapped."""
    x, y = centre(*t)
    return y > 1420 and 360 < x < 730


def use(card, t, have):
    """Card -> the screen dims and the card opens with its name -> the tile: roadblock / monster gone, count -1
    (Fireball: Dminor 2026-11-26, 'Instantly removes the selected roadblock, usable only in this exploration')."""
    tap_wait(CARDS[card], 1780); wait(card, 5)
    tap_wait(*centre(*t)); time.sleep(2)                           # fire / lightning animation
    im = grab(); left = cards(im)[card]
    if left != have - 1 or find(ocr(im), card): raise Stop(f'{card} on row {t[0]} col {t[1]}: count {have} -> {left}, card still open?')
    log(f'    {card} on row {t[0]} col {t[1]} (cards {have} -> {left})')


def stamina(b):
    m = next((re.match(r'^(\d+)/\d+$', t.strip()) for x, y, w, h, t in b if x < 280 and y < 220 and re.match(r'^\d+/\d+$', t.strip())), None)
    return int(m[1]) if m else None


def cave_pink(c):
    r, g, b = c[:3]
    return r > 170 and b > 90 and g < r - 60 and b < r - 10   # a crystal node: magenta; the corner crystals are blue (b >= r)


def cave_left(im):
    """Pink crystal pixels still on the cave board (the 4 corner decorations are blue and off the scan; the portal's
    base is pink too, so its tile is left out)."""
    px, py = CAVE_PORTAL
    return sum(cave_pink(im.getpixel((x, y))) for y in range(460, 1340, 12) for x in range(90, 990, 12)
               if abs(x - px) > 90 or abs(y - py) > 90)


# The cave board: 3-4-5-4-3 tiles, 170 px apart, rows 127 px apart; the portal stands on the centre tile
# (measured on Kratos 2026-11-27; the old fixed portal (540, 1168) is the bottom row's middle tile -> the cave never
# closed and Kratos hung 26 min).
CAVE = [(x0 + 170 * k, 686 + 127 * r) for r, (x0, n) in enumerate([(368, 3), (283, 4), (198, 5), (283, 4), (368, 3)]) for k in range(n)]
CAVE_PORTAL = CAVE.pop(9)


def collect_cave():
    """Mysterious Cave: every tile's item is collected by a tap (Amethyst, gold, ... - Nick 2026-11-27: collect the cave
    loot, then leave). Tap all 18 tiles left to right, top to bottom, then the portal back to the floor.
    ponytail: one cave layout seen (Kratos); the leftover check knows pink crystals only - another item's colour goes
    into cave_pink once one is on screen."""
    for sweep in (1, 2):                                            # a 2nd sweep only when a reward toast ate a tap
        for x, y in CAVE: tap_wait(x, y)
        time.sleep(1.2); im = grab()
        if not find(ocr(im), r'Mysterious Cave'): return log('    Mysterious Cave: not in the cave any more, no portal tap')
        if not cave_left(im): break
    tap_wait(*CAVE_PORTAL); time.sleep(1.5)
    log(f'    Mysterious Cave: {len(CAVE)} tiles tapped x{sweep}, {cave_left(im)} pink left, back through the portal')


def explore():
    """On a floor: tap towards the target until the ruin is finished ('done') or the stamina is out ('stamina')."""
    floor, target, lit, idle, last = None, None, False, 0, None
    while True:
        im = grab(); b = ocr(im)
        if find(b, r'End this exploration'):                      # Ultimate Chest claimed
            tap_wait(*find(b, r'^Exit$')); wait(r'Rewards Overview', 8); tap_wait(540, 1880)
            wait(r'Ruin List', 10); log(f'  floor {floor}: Ultimate Chest, exploration ended'); return 'done'
        if find(b, BUY): tap_wait(938, 636); return 'stamina'   # the 200-diamond offer: X, never Confirm
        if find(b, r'Mysterious Cave'):                           # a side room a tile led into: collect its crystal loot, then the portal back (Nick 2026-11-27)
            collect_cave(); continue
        if find(b, r'Special Event'):                             # an NPC's request popup (Wizard's Request, Dminor 2026-11-26): X - the floors first
            tap_wait(988, 240); time.sleep(1); log('    Special Event popup closed'); continue
        if find(b, r'^Battle$') and find(b, r'Quick Deploy'):     # a monster's lineup screen: fight it (2 stamina)
            if (stamina(b) or 0) < 2: tap_wait(92, 1810); return 'stamina'
            tap_wait(*find(b, r'^Battle$')); b = wait(r'Victory|Defeat|' + BUY, 180)
            if find(b, BUY): tap_wait(938, 636); return 'stamina'
            won = bool(find(b, r'Victory')); tap_wait(540, 1880); time.sleep(1.5); log(f'    monster: {"Victory" if won else "Defeat"}')
            if not won: raise Stop(f'floor {floor}: lost the monster fight')
            continue
        if find(b, r'Congratulations'): time.sleep(0.7); continue   # a reward's toast lies across the tiles: read once it's gone
        if find(b, r'^Floor \d$', (300, 780, 780, 1120)): time.sleep(0.7); continue   # a new floor's name banner lies across rows 4-6 (Dminor: a tile under it read as the target)
        f = next((int(m[1]) for *_, t in b if (m := re.search(r'Floor (\d).?3\b', t))), None)
        st = stamina(b)
        if f is None or st is None: raise Stop(f'not a ruin floor: {joined(b)[:200]}')
        if f != floor: floor, target, lit = f, None, False; log(f'  floor {f}/3, stamina {st}')
        idle = idle + 1 if (st, f) == last else 0; last = (st, f)
        if idle >= 4: raise Stop(f'floor {f}: 4 taps changed nothing (stamina {st})')
        grid, icon, crossed, blocks = read(im)
        if target is None:
            if not icon: raise Stop(f'floor {f}: no door / chest icon found')
            target = icon; log(f'    target row {target[0]} col {target[1]}')
        if target not in grid and target not in crossed:          # explored: the lit door (-> next floor) or chest (-> dialog)
            tap_wait(*centre(*target)); time.sleep(1.2); continue
        if st == 0: return 'stamina'
        d, t = path(grid, target) if target in grid else (None, None)
        # a ruin's last card of a kind waits for a 2-tile saving until the last floor (it may be the only way through a wall)
        worth = lambda n, saved: n and (d is None or saved >= (1 if f == 3 or n > 1 else 2))
        burn = min(((db, x) for x in blocks if target in grid and not coverable(x) and (db := path(grid, target, [x])[0])), default=None)
        if burn and (d is None or burn[0] < d):                   # a roadblock whose removal shortens the way / opens it
            n = cards(im)['Fireball']
            if worth(n, (d or 0) - burn[0]): use('Fireball', burn[1], n); last = None; continue
        dm = path({**grid, **{c: LIGHT for c in crossed}}, target)[0] if crossed else None   # the way with the monster gone
        if dm and (d is None or dm < d):
            m = monster(im, grid, crossed, target, blocks)
            n = cards(im)['Lightning'] if m and not coverable(m) else 0
            if worth(n, (d or 0) - dm): use('Lightning', m, n); last = None; continue
            if m and (d is None or d - dm > 2):                   # no card: the fight's 2 stamina beat the detour
                log(f'    monster in the way at row {m[0]} col {m[1]}: fight'); tap_wait(*centre(*m)); time.sleep(1.5); continue
        if not t: raise Stop(f'floor {f}: no way to the target (roadblocks {sorted(blocks)}, no card / monster to remove)')
        tap_wait(*centre(*t)); time.sleep(0.6)
        im = grab()
        if t != target and edge(im, *t) is None and not near(im.getpixel(centre(*t)), HOLE, 14):   # something on the tile
            _, _, crossed2, blocks2 = read(im)
            if t in blocks2: log(f'    roadblock at row {t[0]} col {t[1]}')
            elif any(x in crossed2 - crossed for x in neighbours(*t)): log(f'    monster at row {t[0]} col {t[1]}')   # dealt with only if it's in the way
            else: tap_wait(*centre(*t)); time.sleep(0.8)          # a reward -> collected (a monster with no X around: its lineup -> fought)


def search(b):
    """Hub with an empty ball: Search when it's free or within SEARCH_CAP. Returns a result word."""
    price = next((int(m[2]) for x, y, w, h, t in b if 1700 < y < 1920 and (m := re.match(r'^(\d+)/(\d+)$', t.strip()))), 0)
    if price > SEARCH_CAP: return f'search costs {price} diamonds (cap {SEARCH_CAP})'
    if price and not PAID_WALKED: return f'search costs {price} diamonds (within the cap; first paid search by hand - not walked yet)'
    tap_wait(*find(b, r'^Search$', (300, 1740, 800, 1900)))
    b = wait(r'^Explore$|Confirm|Cancel', 10)
    if not find(b, r'^Explore$'): raise Stop(f'Search opened a dialog: {joined(b)[:200]}')
    log(f'  search: {"free" if not price else f"PAID {price} diamonds"} -> {" ".join(t for x, y, w, h, t in b if 1080 < y < 1240)}')
    return ''


def run():
    screens = r'Floor \d.?3\b|Ruin List|Quick Deploy'               # a floor, the hub, a monster's lineup
    if not find(ocr(), screens): adventure(r'Ancient Ruins'); time.sleep(2)
    done = 0
    while True:
        b = wait(screens, 12)
        if not find(b, r'Ruin List'):
            if explore() == 'stamina': end = 'out of stamina'; break
            done += 1; continue
        if stamina(b) == 0: end = 'out of stamina'; break
        if find(b, r'^Explore$'): tap_wait(*find(b, r'^Explore$')); continue
        if end := search(b): break
    for _ in range(3):                                            # floor / hub back arrow -> main screen
        if is_main(): break
        tap_wait(92, 1810); time.sleep(1.5)
    log(f'ruins done: {done} finished, {end}')


if __name__ == '__main__':
    main(run)
