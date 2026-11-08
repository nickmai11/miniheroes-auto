#!/usr/bin/env python3
# Relics (Archaeology dig board): spend every shovel by the relic skill's value model, no LLM (Nick, 2026-11-03).
# usage: D=<serial> scripts/relic.py <account> [--dry] [--max-digs N]   (main screen, the Lost Continent map or the
#        board; --max-digs 0 = boosters only, on the current board;
#        board; ends on the main screen; --dry = read + plan only, no tap; exit 1 = stopped early, see v_relic.png)
#        scripts/relic.py --boards PNG...            offline: print each screenshot's board + plan (no device)
#        scripts/relic.py --learn PNG rN cM LABEL    add that cell as a tile exemplar (relic_tiles/LABEL.<n>.png) —
#                                                    only after looking at the cell; never from r6c1 (the % label)
# Reading: each of the 42 cells is matched against the exemplar crops in relic_tiles/ (nearest 24x24 thumb);
# no exemplar within THRESH -> '?' = never dug, never crossed (reported). Two consecutive reads must agree
# (reward banners / dig dust). Shovel counter and banners by OCR (flow.ocr).
# Planning (skill: "every dig needs a target"): a lit pickaxe is dug first (free; in the bottom row it reveals a row);
# then Dijkstra over dig costs (pickaxe 0) from the lit (diggable) cells, over the board plus the hidden row below it
# (HIDDEN per tile: a cheaper corridor there -> the first dig is the dig-down that shows it, Nick 2026-11-04); the item
# with the best value/cost >= RATIO is the target, its first path cell is dug; nothing worth it -> the cheapest
# bottom-row dig (reveals a new row). A bottom-row dig scrolls row 1 off for good: an item there worth its route goes first. Boosters, One-Tap Mining, the shovel "+" are never tapped; the milestone reward is claimed.
# Boosters (skill rule; mechanics verified 2026-11-04): after the digs, dynamite/drill are DRAGGED onto the board where
# they save >= SAVES shovels (booster_plan), verified by the badge; otherwise a hint line.
import glob, os, re, sys, time, heapq
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
TILES = os.path.join(HERE, 'relic_tiles')
X = [116, 284, 452, 624, 794, 962]                      # cell centres, device coords (1080x1920)
Y = [600, 770, 940, 1110, 1280, 1450, 1620]
H, T = 72, 24                                             # cell crop half-size, thumb size
THRESH, MARGIN = 14.0, 4.0                                # max thumb distance to accept; 2nd-best label must be this far
# frame pixels that are identical on every saved board (56 screenshots): the board is on screen and no popup dims it
FRAME = {(22, 1512): (173, 134, 107), (1058, 1512): (115, 81, 58), (540, 512): (74, 61, 58), (14, 1000): (107, 89, 82),
         (60, 392): (74, 69, 66)}
# label -> (kind, lit). kinds: . empty  D dirt  S stone(2 hits)  K cracked stone  R shard  C relic chest  G gold chest
# (Moon Essence, worth 0)  P pickaxe (shovel back)  M multi-square chest  ? unknown
KINDS = {'empty': ('.', False), 'pit': ('.', False), 'dirt': ('D', None), 'stone': ('S', None), 'cracked': ('K', None),
         'shard': ('R', None), 'chest': ('C', None), 'gold': ('G', None), 'pick': ('P', None), 'multi': ('M', None),
         'frame': ('.', False)}   # gold-frame tile of a multi chest without the chest art: read() joins it to the art it touches
COST = {'D': 1, 'K': 1, 'S': 2, 'R': 1, 'C': 1, 'G': 1, 'P': 0, 'M': 0}   # pickaxe: its shovel comes back -> net 0;
                                                                         # multi chest: always opens for free (Nick 2026-11-04; Cmajor: shovels 1->1, Mine bar unchanged)
VALUE = {'R': 0.28, 'C': 1.6, 'M': 3.2, 'G': 0.0}  # base-relic units. Multi chest: the most important item, above the relic chest (Nick 2026-11-04) -> target() takes its routes first, whatever the ratio. Chest 1.6 = measured 2026-11-04 (29 base + 4 fused of 33,
                                                   # a fused Common = 6 base by fusion). Shard: measured 0.21, kept at Nick's 0.28 (see
                                                   # skill). Pickaxe = free tile, not a target.
RATIO = 0.14                                               # units per shovel a target must beat (measured r ~0.13-0.15)
ITEMS = re.compile(r'((?:Limestone|Beast Bone|Bronze Mirror|Stone Hammer|Bone Saw|Bronze Dagger|Moon Essence|Legend Spiritstone)'
                   r'(?: Fragment)?)\s*[Xx×]\s*(\d+)')   # "Limestone FragmentX3" = shard, "Limestone X1" = whole relic (chest)


# ---------- reading ----------

def thumb(im, r, c):
    x, y = X[c], Y[r]
    return np.asarray(im.crop((x - H, y - H, x + H, y + H)).resize((T, T), Image.BILINEAR), dtype=np.float32)


def mask(r, c):
    """r6c1 carries the yellow '77.54%' label over its bottom third -> ignore that band there."""
    m = np.ones((T, T, 1), dtype=np.float32)
    if (r, c) == (5, 0): m[16:] = 0
    return m


_tiles = None
def tiles():
    global _tiles
    if _tiles is None:
        _tiles = []
        for f in sorted(glob.glob(os.path.join(TILES, '*.png'))):
            label = os.path.basename(f).split('.')[0]
            im = Image.open(f).convert('RGB')
            _tiles.append((label, np.asarray(im.resize((T, T), Image.BILINEAR), dtype=np.float32)))
        if not _tiles: raise SystemExit(f'no exemplars in {TILES}')
    return _tiles


def cell(im, r, c):
    """-> (kind, lit, label, dist). '?' when no exemplar is close or two labels are nearly as close."""
    t, m = thumb(im, r, c), mask(r, c)
    best = {}
    for label, e in tiles():
        d = float((np.abs(e - t) * m).sum() / (m.sum() * 3))
        if d < best.get(label, 1e9): best[label] = d
    ranked = sorted(best.items(), key=lambda kv: kv[1])
    label, d = ranked[0]
    if d > THRESH or (len(ranked) > 1 and ranked[1][1] - d < MARGIN and ranked[1][0].split('_')[0] != label.split('_')[0]):
        return '?', False, label, d
    kind, lit = KINDS[label.split('_')[0]]
    if lit is None: lit = label.endswith('_lit')
    return kind, lit, label, d


def light(g):
    """A tile beside a dug cell is diggable whatever shade it was read as — the game's own rule; shade and adjacency agree
    on every eye-checked board. Kong 2026-11-04: a bottom-row gold chest read dark hid 2 shards behind it (Nick)."""
    return [[(k, lit or (k not in '.?' and any(0 <= r + dr < 7 and 0 <= c + dc < 6 and g[r + dr][c + dc][0] == '.'
                                               for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)))))
             for c, (k, lit) in enumerate(row)] for r, row in enumerate(g)]


def read(im):
    """7x6 grid of (kind, lit). A multi chest = one gold frame over 2/4/6 tiles with the chest art on only some of them
    (2x2 silver: its lower tiles, Aminor 2026-11-04; 2x3 red: the bottom-middle tile, Cmajor 2026-11-04). Its plain
    frame tiles ('frame') look exactly like its opened golden pit -> a frame block touching an 'M' is all that chest;
    a frame block with no art is a pit (empty)."""
    cells = [[cell(im, r, c) for c in range(6)] for r in range(7)]
    g = [[k[:2] for k in row] for row in cells]
    chests = []
    todo = {(r, c) for r in range(7) for c in range(6) if cells[r][c][2].startswith('frame') or g[r][c][0] == 'M'}
    while todo:
        comp, stack = set(), [todo.pop()]
        while stack:
            r, c = stack.pop(); comp.add((r, c)); todo.discard((r, c))
            stack += [q for q in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)) if q in todo]
        art = [g[r][c] for r, c in comp if g[r][c][0] == 'M']
        for r, c in comp: g[r][c] = ('M', any(lit for _, lit in art)) if art else ('.', False)
        if art: chests.append(comp)
    g = light(g)
    for comp in chests:                 # one chest: lit as a whole when any of its tiles is (Cmajor 2026-11-05: a dark 2x1
        if any(g[r][c][1] for r, c in comp):   # chest read lit was tapped and refused)
            for r, c in comp: g[r][c] = ('M', True)
    return g


def show(g):
    """Text board: uppercase = lit (diggable now), lowercase = dark; '.' empty, '?' unknown."""
    return '\n'.join(' '.join(k if k in '.?' else (k if lit else k.lower()) for k, lit in row) for row in g)


def on_board(im): return all(max(abs(a - b) for a, b in zip(im.getpixel(p), c)) <= 12 for p, c in FRAME.items())


# ---------- planning ----------

HIDDEN = 0.99   # assumed dig cost of a tile in the still-hidden row below the board (see routes); just under dirt, so
                # a toss-up between a known tunnel and "dig down and look" goes to looking (Nick 2026-11-04)
NAME = {'R': 'shard', 'C': 'relic chest', 'M': 'multi chest'}


def routes(g, blocked=()):
    """Dijkstra from the lit cells (cost = that cell's own dig cost) through diggable kinds; '?' and blocked cells are
    walls. A row past the 7th is the hidden row a bottom-row dig would reveal, at HIDDEN per tile: a corridor there can
    beat a known route through stone, so the plan's first step becomes the dig-down that shows it (Nick 2026-11-04:
    "dig down to see the path before choosing the hard way"). -> (dist, prev)."""
    INF = 1e9
    def cost(r, c):
        k = g[r][c][0]
        return INF if k in '.?' or (r, c) in blocked else HIDDEN if r >= 7 else COST[k]
    def key(r, c):   # search cost: an item tile is free to pass through, so of two routes of equal real cost the one that
        k = g[r][c][0]   # collects shards/chests wins (Chien Than 2026-11-04: a 5-dig tunnel past 2 gold chests was chosen
        return 0 if r < 7 and VALUE.get(k, 0) > 0 else cost(r, c)   # over the 5-dig bottom row with 2 shards, Nick)
    # kd = (search cost, real cost, -bottom-row digs): equal search costs go to the cheaper real route, then to the one
    # with more bottom-row digs - each reveals a row (Dminor 2026-11-05, Nick: the dirt above a shard was dug while the
    # bottom tile beside the shaft reached it for the same 2 shovels)
    dist, kd, prev, q, NONE = {}, {}, {}, [], (INF, INF, 0)
    for r in range(len(g)):
        for c in range(6):
            if g[r][c][1] and cost(r, c) < INF:
                dist[(r, c)] = cost(r, c); kd[(r, c)] = (key(r, c), cost(r, c), -(r == 6 and cost(r, c) > 0)); prev[(r, c)] = None
                heapq.heappush(q, (kd[(r, c)], r, c))
    while q:
        d, r, c = heapq.heappop(q)
        if d > kd.get((r, c), NONE): continue
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if not (0 <= nr < len(g) and 0 <= nc < 6) or cost(nr, nc) >= INF: continue
            nd = (d[0] + key(nr, nc), d[1] + cost(nr, nc), d[2] - (nr == 6 and cost(nr, nc) > 0))   # paid digs only: free pickaxe steps must not loop
            if nd < kd.get((nr, nc), NONE):
                kd[(nr, nc)] = nd; dist[(nr, nc)] = nd[1]; prev[(nr, nc)] = (r, c); heapq.heappush(q, (nd, nr, nc))
    return dist, prev


def path(prev, t):
    """Route to t: the target first, the lit cell to dig now last."""
    out = []
    while t is not None: out.append(t); t = prev[t]
    return out


def multi_groups(g):
    """cell -> id of its connected 'M' block: a multi-square chest is ONE item over 2/4/6 tiles (Aminor 2026-11-04)."""
    comp, n = {}, 0
    for r in range(len(g)):
        for c in range(len(g[r])):
            if g[r][c][0] == 'M' and (r, c) not in comp:
                n += 1; stack = [(r, c)]
                while stack:
                    a, b = stack.pop()
                    if (a, b) in comp or not (0 <= a < len(g) and 0 <= b < len(g[a])) or g[a][b][0] != 'M': continue
                    comp[(a, b)] = n; stack += [(a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)]
    return comp


def target(g, dist, prev, blocked=(), rows=range(7)):
    """The item in `rows` with the best value/cost >= RATIO -> (r, c, why) of its first dig, or None. The shovels left
    don't matter (Nick 2026-11-04: they recover; a half-dug tunnel is finished by the next run)."""
    worth = lambda r, c: g[r][c][0] in VALUE and VALUE[g[r][c][0]] > 0 and (r, c) not in blocked
    comp = multi_groups(g)
    best = None
    for (r, c), d in dist.items():
        if r not in rows or not worth(r, c): continue
        # shared tunnel (Nick 2026-11-03: a gold chest is a fine stepping stone to 2+ shards): unlit items beside the
        # route become 1 dig each once it's dug -> they count toward this route's value and cost
        p = path(prev, (r, c))
        extra = {(nr, nc) for pr, pc in p for nr, nc in ((pr + 1, pc), (pr - 1, pc), (pr, pc + 1), (pr, pc - 1))
                 if 0 <= nr < 7 and 0 <= nc < 6 and (nr, nc) not in p and not g[nr][nc][1] and worth(nr, nc)}
        seen = set()
        def once(a, b):   # items on the way count too; a multi chest's tiles: value once per route, its other tiles cost 0
            k = g[a][b][0]
            if k != 'M': return VALUE.get(k, 0), COST.get(k, 0)
            if comp[(a, b)] in seen: return 0, 0
            seen.add(comp[(a, b)]); return VALUE['M'], COST['M']
        v = sum(once(a, b)[0] for a, b in p); ex = [once(a, b) for a, b in extra]
        v += sum(x[0] for x in ex); cst = d + sum(x[1] for x in ex)
        if cst <= 0: continue                                     # a free (lit) chest is _next()'s job
        multi = g[r][c][0] == 'M'                                 # Nick 2026-11-04: a multi chest outranks everything, at any cost
        key = (multi, v / cst, -cst, r)
        if (multi or v / cst >= RATIO - 1e-9) and (best is None or key > best[0]): best = (key, (r, c), d, len(extra), v / cst, p)
    if not best: return None
    (r, c), d, n, ratio, p = best[1:]
    return p[-1][0], p[-1][1], (f'route to {NAME[g[r][c][0]]} r{r + 1}c{c + 1}{f" +{n} beside it" if n else ""}'
                                f'{" via the next row" if any(a >= 7 for a, b in p) else ""}, cost {d:.0f}, {ratio:.2f}/shovel')


def plan(g, blocked=()):
    """-> (r, c, why) for the next dig, or None: a lit pickaxe (free), else the best item by value/cost (>= RATIO) over
    the board plus its hidden next row, else the cheapest bottom-row dig. A bottom-row dig scrolls row 1 off the board
    for good, so an item there that is worth its route goes first (Nick 2026-11-04: "collect the resources at the top
    before going down")."""
    nxt = _next(g, blocked)
    if nxt and nxt[0] == 6:
        dist0, prev0 = routes(g, set(blocked) | {(6, c) for c in range(6)})            # routes that don't scroll
        top = target(g, dist0, prev0, blocked, rows=(0,))
        if top: return top[0], top[1], top[2] + ', before the scroll loses it'
        lost = [f'{NAME[g[0][c][0]]} r1c{c + 1} ({f"cost {dist0[(0, c)]:.0f}" if (0, c) in dist0 else "no route"})'
                for c in range(6) if g[0][c][0] in NAME]
        if lost: nxt = nxt[0], nxt[1], nxt[2] + f'; letting {", ".join(lost)} go (not worth it)'
    return nxt


def _next(g, blocked):
    # a lit pickaxe costs nothing net; one in the bottom row reveals a new row before we commit to a route
    # (Nick 2026-11-04, Kong: the script dug a 7-shovel tunnel to a chest while a free pickaxe sat lit in the bottom row)
    # a lit multi chest opens for free (Cmajor 2026-11-04) -> first of all
    free = [(r, c) for r in range(7) for c in range(6) if g[r][c][0] in 'PM' and g[r][c][1] and (r, c) not in blocked]
    if free:
        r, c = min(free, key=lambda p: (g[p[0]][p[1]][0] != 'M', p[0] != 0, -p[0]))   # chest, then row 1 (the next scroll loses it), else bottom first
        if g[r][c][0] == 'M': return r, c, f'multi chest r{r + 1}c{c + 1} (opens free)'
        return r, c, f'free pickaxe r{r + 1}c{c + 1}' + (' (reveals a row)' if r == 6 else '')
    g8 = g + [[('D', False)] * 6]                                   # the hidden row a bottom-row dig reveals (HIDDEN per tile)
    dist, prev = routes(g8, blocked)
    t = target(g8, dist, prev, blocked)
    if t: return t
    bottom = [(d, g[6][c][0] != 'D', abs(c - 2.5), c) for c in range(6) for d in [dist.get((6, c))] if d is not None]
    if not bottom: return None
    d, _, _, c = min(bottom)
    fr, fc = path(prev, (6, c))[-1]
    return fr, fc, f'dig down via r7c{c + 1}, cost {d:.0f}' if (fr, fc) != (6, c) else f'dig down r7c{c + 1}, cost {d:.0f}'

BOOST = {'dynamite': 766, 'drill': 310}   # bottom-bar buttons (x; y 1820): DRAG one onto a dug tile — a tap does nothing


def stock(im):
    """Booster badges (small digits under the buttons) -> {'drill': n, 'dynamite': n}; a kind is missing when unreadable.
    Each badge is cropped and scaled x3 onto a blank screen and OCRed there: the full-screen OCR read the drill's '130'
    as '732' or not at all (2026-11-04)."""
    canvas, out = Image.new('RGB', (1080, 1920)), {}
    for i, (k, x) in enumerate(BOOST.items()):
        canvas.paste(im.crop((x - 90, 1830, x + 90, 1900)).resize((540, 210), Image.BILINEAR), (0, 300 * i))
    for b in ocr(canvas):
        m = re.fullmatch(r'\D*(\d+)\D*', b[4])
        if m and b[1] < 600: out[list(BOOST)[int(b[1]) // 300]] = int(m.group(1))
    return out


SAVES = 6                                                           # fire a booster when it saves this many shovels (Nick 2026-11-04: one number)


def booster_plan(g, blocked=()):
    """Candidates (shovels saved, kind, r, c), best first. Mechanics verified on the Kong instance 2026-11-04: dynamite
    digs the diamond of radius 2 around the drop tile; the drill digs the whole bottom row (its column is only the
    preview); stone goes in one hit; a booster that digs any bottom-row tile scrolls the board one row. Saved = per item
    collected the cheaper of its hand-dig cost and its worth in shovels (VALUE/RATIO, pickaxe 1), +1 for the row a scroll
    reveals, minus the row-1 items the planner would still have collected (the scroll loses them)."""
    dist, _ = routes(g, blocked); comp = multi_groups(g); seen = set()
    def saved(r, c):
        k = g[r][c][0]
        if k == 'P': return 1
        if k == 'M' and comp[(r, c)] in seen: return 0   # a multi chest (2/4/6 tiles) opens once: Aminor 2026-11-04 dynamite -> golden pit
        if k == 'M': seen.add(comp[(r, c)])
        return min(dist.get((r, c), 1e9), VALUE[k] / RATIO) if VALUE.get(k, 0) > 0 else 0
    def kept(c):                                   # a row-1 item the planner would still collect -> lost at a scroll
        k, d = g[0][c][0], dist.get((0, c))
        if d is None: return 0
        if k == 'P': return 1 if g[0][c][1] else 0
        return d if VALUE.get(k, 0) / d >= RATIO - 1e-9 else 0
    scroll = 1 - sum(kept(c) for c in range(6))
    empties = [(r, c) for r in range(7) for c in range(6) if g[r][c][0] == '.']
    def total(cells):
        seen.clear(); return sum(saved(a, b) for a, b in cells)
    cands = [(total([(a, b) for a in range(7) for b in range(6) if abs(a - r) + abs(b - c) <= 2]) + (scroll if r >= 4 else 0),
              'dynamite', r, c) for r, c in empties]
    if empties: cands.append((total([(6, c) for c in range(6)]) + scroll, 'drill', *empties[0]))
    return sorted(cands, reverse=True)


def booster_hint(g, im=None):
    c = booster_plan(g)
    if not c: return 'booster hint: no dug tile to drop on'
    s, kind, r, c0 = c[0]
    return f'booster hint (not used): best {kind} r{r + 1}c{c0 + 1} saves ~{s:.0f} shovels' + (f', stock {stock(im)}' if im else '')


def boosters(g, blocked, im, got):
    """Fire late (Nick 2026-10-30): after the digs, the best booster while it saves >= SAVES shovels; each firing is
    verified by the badge going down by 1. -> (grid, image) afterwards."""
    for _ in range(3):
        st, cands = stock(im), booster_plan(g, blocked)
        pick = next(((s, k, r, c) for s, k, r, c in cands if st.get(k) and s >= SAVES - 1e-9), None)
        if not pick:
            if cands: s, k, r, c = cands[0]; log(f'booster hint (not used): best {k} r{r + 1}c{c + 1} saves ~{s:.0f} shovels, stock {st}')
            return g, im
        s, k, r, c = pick
        swipe(BOOST[k], 1820, X[c], Y[r], 700); time.sleep(1.2)
        b2 = ocr()
        if dismiss(b2): b2 = ocr()
        reward = ' '.join(f'{m.group(1)} x{m.group(2)}' for m in ITEMS.finditer(joined(b2)))
        g2, im = stable_board()
        if g2 is None: raise Stop('left the dig board after a booster')
        st2 = stock(im)
        if st2.get(k) is None: time.sleep(1); im = grab(); st2 = stock(im)   # badge OCR misses (Tiger 2026-11-06: drill fired, read None)
        fired = st2.get(k) == st[k] - 1 or (st2.get(k) is None and g2 != g)  # unreadable badge: the board changing is the proof
        log(f'{k} r{r + 1}c{c + 1} (saves ~{s:.0f}, stock {st[k]}->{st2.get(k)}{"" if st2.get(k) is not None else ", board changed" if g2 != g else ""}) -> {reward or "no banner"}')
        if reward: got.append(reward)
        if not fired: log('booster not consumed -> no more boosters'); return g2, im
        g, blocked = g2, set()                                   # a scroll moved everything: stale blocked cells
    return g, im

# ---------- device ----------

def log(msg):
    print(msg, flush=True)
    if LOG:
        with open(LOG, 'a') as f: f.write(f'{time.strftime("%F %T")} [relic] {msg}\n')


def shovels(boxes):
    """'66/150' counter top-left -> (66, 150), or None."""
    m = re.search(r'(\d+)\s*/\s*(\d+)', ' '.join(b[4] for b in boxes if 360 < b[1] < 425 and b[0] < 300))
    return (int(m.group(1)), int(m.group(2))) if m else None


def stable_board(tries=12):
    """Grab until two consecutive reads agree (banners, dust, scroll); reward popups are closed on the way.
    -> (grid, image), or (None, image) when some other screen is up; Stop if never stable."""
    prev = None
    for _ in range(tries):
        im = grab()
        if not on_board(im):
            if dismiss(ocr(im)): prev = None; continue
            return None, im
        g = read(im)
        if g == prev: return g, im
        prev = g; time.sleep(0.35)
    raise Stop('board never settled (12 reads)')


def open_board():
    """Main screen / Lost Continent map / popup / other screen (back arrow) -> the dig board."""
    loading = False            # True right after our own navigation tap: the next screen gets one pass to draw
    for _ in range(10):
        im = grab()
        if on_board(im): return
        boxes = ocr(im)
        if is_main(im): tap_wait(972, 1788); time.sleep(0.5); loading = True; continue
        a = find(boxes, r'Archaeology')
        if a: tap_wait(*a); time.sleep(0.5); loading = True; continue
        if find(boxes, r'Tap anywhere|Do not remind'): tap_wait(540, 120); continue
        if find(boxes, r'Shovel\?|Remaining purchases'): tap_wait(938, 636); time.sleep(0.5); continue   # shovel Tip left open
        # any other screen (Tribe left by catch-up, Dino/Dminor/Bino 2026-11-04): back arrow at once, no waiting
        if loading: time.sleep(1); loading = False
        else: tap_wait(80, 1820); time.sleep(0.6)
    raise Stop(f'could not reach the dig board; screen: {joined(ocr())[:160]}')


def leave():
    for _ in range(4):
        if is_main(grab()): return True
        tap_wait(80, 1820); time.sleep(0.6)
    return is_main(grab())


def is_main(im): return max(abs(a - b) for a, b in zip(im.getpixel((92, 1788)), (0, 158, 230))) <= 40


def dismiss(boxes):
    """Reward popups (multi chest, milestone) -> tap anywhere; True if one was up."""
    if find(boxes, r'Tap anywhere to close|Congratulations'):
        tap_wait(540, 120); time.sleep(0.4); return True
    return False


def benefit():
    """Board's Benefit icon (top-right) with a red dot -> open, tap the yellow Claim (daily login: 1 dynamite, 1 drill,
    15 shovels on pass accounts), close. Never the purchase button (Nick 2026-11-04: check Benefit before digging)."""
    im = grab()
    dot = sum(1 for y in range(360, 420, 3) for x in range(1020, 1075, 3)
              if (lambda q: q[0] > 210 and q[1] < 70 and q[2] < 100)(im.getpixel((x, y))))
    if dot < 4: return 'benefit: no red dot'
    tap_wait(1015, 430); boxes = ocr(); t0 = time.time()
    while not find(boxes, r'^Benefit$') and time.time() - t0 < 6: time.sleep(0.4); boxes = ocr()
    if not find(boxes, r'^Benefit$'): raise Stop(f'Benefit did not open; screen: {joined(boxes)[:120]}')
    got = 'benefit: nothing to claim (button grey / absent)'
    im = grab(); boxes = ocr(im)
    for x, y, w, h, t in boxes:
        q = im.getpixel((x - 14, y + h // 2))            # button colour left of the text: green "Claim Reward" (xFaktor
        if re.fullmatch(r'Claim( Reward)?', t.strip()) and y > 1500 and \
                max(q) - min(q) > 60 and q[0] < 240:     # 2026-11-04) or yellow; grey "Claimed" has no saturation
            tap_wait(x + w // 2, y + h // 2); time.sleep(0.8); b2 = ocr()
            got = 'benefit: claimed' + (' (reward popup closed)' if dismiss(b2) else '')
            break
    for _ in range(3):                                   # X, until the Benefit dialog is really gone
        tap_wait(974, 240); time.sleep(0.5)
        if not find(ocr(), r'^Benefit$'): break
    return got


def buy_shovels(prices, account):
    """Shovel + (green, on the shovel button) -> Tip "Spend N diamonds to buy 10 Shovel? (Remaining purchases: k)".
    Confirm only while N is one of the account's configured prices (relic_shovel_buys, Nick 2026-11-04: default 80;
    Kong 80/160/240; Cmajor 80/160) and the gem counter covers it; any other price -> X, stop. Each buy is verified by
    the shovel counter (+10)."""
    # per game day: prices bought + the next price seen -> a re-run doesn't open the Tip again (Nick 2026-11-04: "you
    # seem to have clicked too many times on the buy shovels" - every pass re-opened and closed it to read the price)
    day = time.strftime('%F', time.gmtime(time.time() - 5 * 3600))
    st = f'/tmp/miniheroes-state/{account}-{day}.relic_buys'; os.makedirs('/tmp/miniheroes-state', exist_ok=True)
    done = [int(x) for x in open(st).read().split()] if os.path.exists(st) else []
    bought, nxt = [x for x in done if x > 0], [-x for x in done if x < 0]       # negative = the next price seen (not bought)
    left = [x for x in prices if x not in bought]
    if not left or (nxt and nxt[-1] not in left):
        return f'shovel buy: nothing left today (bought {bought}, next price {nxt[-1] if nxt else "?"})'
    out = []
    tip = lambda boxes: re.search(r'Spend\D*(\d+)\D+buy\D*(\d+)\s*Shovel', joined(boxes))
    boxes = ocr()
    while left:
        n0 = shovels(boxes) or (0, 0)
        if not tip(boxes):                               # after a Confirm the Tip stays open with the NEXT price (Bino 2026-11-04) -> no + tap then
            tap_wait(656, 1770); boxes = ocr(); t0 = time.time()
            while not tip(boxes) and time.time() - t0 < 4: time.sleep(0.4); boxes = ocr()
        m = tip(boxes)
        if not m:
            out.append(f'shovel buy: no price popup ({joined(boxes)[:80]})'); dismiss(boxes); break
        price, cnt = int(m.group(1)), int(m.group(2))
        gm = re.search(r'(\d+)', ' '.join(b[4] for b in boxes if b[1] < 90 and b[0] < 320))
        gems = int(gm.group(1)) if gm else -1
        if price not in left or gems < price:
            open(st, 'a').write(f' -{price}'); out.append(f'shovel buy skipped: {price} gems on screen not in {left} (gems {gems})'); break
        tap_wait(540, 1162); time.sleep(1.2)             # Confirm
        boxes = ocr(); n1 = shovels(boxes) or n0
        if n1[0] < n0[0] + cnt: raise Stop(f'shovel buy at {price}: counter {n0[0]} -> {n1[0]}, expected +{cnt}')
        open(st, 'a').write(f' {price}'); left.remove(price); out.append(f'bought {cnt} shovels for {price} gems ({n0[0]} -> {n1[0]})')
    for _ in range(3):                                   # X on a Tip left open (the next price)
        if not tip(boxes): break
        tap_wait(938, 636); time.sleep(0.5); boxes = ocr()
    return '; '.join(out) or 'shovel buy: none configured'


def topup(account):
    """Out of free shovels -> Benefit red dot (Claim) + the configured shovel buys, ONCE per game day (Nick 2026-11-04:
    "benefit check and buy only when out of shovel, only once per day"); marker /tmp/miniheroes-state/<acct>-<day>.relic_topup."""
    day = time.strftime('%F', time.gmtime(time.time() - 5 * 3600))
    st = f'/tmp/miniheroes-state/{account}-{day}.relic_topup'; os.makedirs('/tmp/miniheroes-state', exist_ok=True)
    if os.path.exists(st): return f'top-up: done today ({open(st).read().strip()[:120]})'
    y = open(os.path.join(HERE, '..', 'accounts', account + '.yaml')).read()
    m = re.search(r'^\s*relic_shovel_buys:\s*\[([^\]]*)\]', y, re.M)
    prices = [int(x) for x in re.findall(r'\d+', m.group(1))] if m else [80]
    r = benefit() + '; ' + buy_shovels(prices, account)
    open(st, 'w').write(r)
    return 'top-up: ' + r


def run(account, dry=False, max_digs=None):
    open_board()
    g, im = stable_board()
    if g is None: raise Stop('not on the dig board')
    boxes = ocr(im)
    n = shovels(boxes)
    if n is None: raise Stop('cannot read the shovel counter')
    ms = re.search(r'Mine (\d+) more', joined(boxes))
    unknown = lambda g: ' '.join(f'r{r + 1}c{c + 1}' for r in range(7) for c in range(6) if g[r][c][0] == '?')
    log(f'start {account}: shovels {n[0]}/{n[1]}, milestone {ms.group(1) if ms else "?"} more'
        + (f', UNKNOWN cells {unknown(g)}' if unknown(g) else ''))
    log('board:\n' + show(g))
    if dry:
        p = plan(g); log(f'plan: {p and f"r{p[0] + 1}c{p[1] + 1} ({p[2]})"}'); log(booster_hint(g, im)); return 0
    digs, blocked, refused, got = 0, set(), 0, []
    cap = n[0] + 60 if max_digs is None else max_digs            # pickaxe refunds + regen add digs; 60 is a hard stop
    topped = False
    while True:
        while n[0] > 0 and digs < cap:                                  # until the counter reads 0 (Aminor: 3 left over when it counted digs)
            if re.search(r'Mine 0 more', joined(boxes)):                  # milestone reward ready -> claim (free)
                tap_wait(1010, 280); time.sleep(0.6); b2 = ocr()
                log('milestone claim -> ' + (f'got: {joined(b2)[:100]}' if dismiss(b2) else 'no popup: ' + joined(b2)[:80]))
                g, im = stable_board()
                if g is None: raise Stop('left the dig board after the milestone claim')
                boxes = ocr(im)
            p = plan(g, blocked)
            if p is None: log(f'nothing diggable (lit cells unknown/blocked: {unknown(g) or "-"}) -> stop'); break
            r, c, why = p
            k0 = g[r][c]; n0 = n[0]
            b2 = ocr(tap_wait(X[c], Y[r]))                                # banner "Limestone FragmentX2" shows right after
            if dismiss(b2):                                               # multi chest reward popup: log its own text (Kong 2026-11-05 logged the board header)
                t = joined(b2); i = t.find('Congratulations'); j = t.find('Tap anywhere')
                log(f'  popup: {t[i:i + 160] if i >= 0 else t[max(j - 160, 0):j + 12]}'); b2 = ocr()
            if find(b2, r'adjacent plot'):
                blocked.add((r, c)); refused += 1; log(f'dig r{r + 1}c{c + 1} refused ("adjacent plot") -> blocked')
                if refused >= 3: raise Stop('3 refused digs')
                g, im = stable_board(); boxes = ocr(im); continue
            g2, im = stable_board()
            if g2 is None and find(ocr(im), r'fully excavated'):   # last tile of the area: game jumps to Relic Display (Dino 2026-11-08)
                log(f'dig r{r + 1}c{c + 1} {k0[0]} ({why}) -> area fully excavated, re-entering Archaeology (next area)')
                digs += 1; open_board(); g, im = stable_board(); boxes = ocr(im); n = shovels(boxes) or n
                if g is None: raise Stop('not on the dig board after the area change')
                continue
            if g2 is None: raise Stop('left the dig board after a tap')
            boxes = ocr(im); n2 = shovels(boxes) or n
            reward = ' '.join(f'{m.group(1)} x{m.group(2)}' for m in ITEMS.finditer(joined(b2)))
            changed = lambda: g2[r][c] != k0 or (r == 6 and g2 != g)
            if not changed() and n2[0] >= n0 and k0[0] != 'P':
                time.sleep(1.5); g2, im = stable_board(); boxes = ocr(im); n2 = shovels(boxes) or n   # late tap?
                if not changed() and n2[0] >= n0:
                    blocked.add((r, c)); refused += 1
                    log(f'dig r{r + 1}c{c + 1} {k0[0]}: no effect (shovels {n0}->{n2[0]}) -> blocked')
                    if refused >= 3: raise Stop('3 digs without effect')
                    g = g2; continue
            digs += 1; refused = 0
            if reward: got.append(reward)
            after = f'scrolled, now {g2[r][c][0]}' if r == 6 else g2[r][c][0]
            log(f'dig r{r + 1}c{c + 1} {k0[0]} ({why}) -> {reward + ", " if reward else ""}{after}; shovels {n0}->{n2[0]}')
            g, n = g2, n2

        if topped or max_digs is not None or n[0] > 0: break   # only when the shovels are out: Benefit + buys, once per game day (Nick 2026-11-04)
        topped = True; log(topup(account))
        g, im = stable_board()
        if g is None: raise Stop('not on the dig board after the top-up')
        boxes = ocr(im); n = shovels(boxes) or n
        if n[0] == 0: break
        cap = digs + n[0] + 60
    g, im = boosters(g, blocked, im, got)                         # fire late, by the rule
    log(f'done: {digs} digs, shovels {n[0]}/{n[1]} left, items: {", ".join(got) or "none"}'
        + (f', UNKNOWN cells {unknown(g)}' if unknown(g) else '') + '\n' + show(g))
    if not leave(): raise Stop('not back on the main screen')
    return 0 if n[0] == 0 or (max_digs is not None and digs >= max_digs) else 1


def learn(png, r, c, label):
    im = Image.open(png).convert('RGB'); r, c = int(r) - 1, int(c) - 1
    k = cell(im, r, c)
    n = max([int(f.split('.')[-2]) for f in glob.glob(os.path.join(TILES, label + '.*.png'))] + [0]) + 1   # gaps: count+1 overwrote multi_lit.3 (2026-11-04)
    out = os.path.join(TILES, f'{label}.{n}.png')
    im.crop((X[c] - H, Y[r] - H, X[c] + H, Y[r] + H)).save(out)
    print(f'{out}: nearest before = {k[2]} ({k[3]:.1f})')


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['--learn']: learn(*a[1:5]); sys.exit()
    if a[:1] == ['--boards']:
        for f in a[1:]:
            im = Image.open(f).convert('RGB')
            if im.size != (1080, 1920): full = Image.new('RGB', (1080, 1920)); full.paste(im, (0, 510)); im = full   # board crop (relic_tiles/boards)
            g = read(im); p = plan(g)
            print(f'{os.path.basename(f)}  board={on_board(im)}\n{show(g)}\nplan: {p and f"r{p[0] + 1}c{p[1] + 1} ({p[2]})"}\n')
        sys.exit()
    sys.path.insert(0, HERE)
    from tap import grab, tap as tap_wait
    from flow import Stop, find, joined, ocr, main, swipe
    ACCOUNT = a[0]; dry = '--dry' in a
    mx = int(a[a.index('--max-digs') + 1]) if '--max-digs' in a else None
    day = time.strftime('%F', time.gmtime(time.time() - 5 * 3600))
    LOG = None if os.environ.get('ACCOUNT') else os.path.join(HERE, '..', 'logs', ACCOUNT, day + '.log')  # daily.py tees itself
    if LOG: os.makedirs(os.path.dirname(LOG), exist_ok=True)
    main(run, ACCOUNT, dry, mx)
else:
    LOG = None
