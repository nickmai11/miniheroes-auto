#!/usr/bin/env python3
# Relics (Archaeology dig board): spend every shovel by the relic skill's value model, no LLM (Nick, 2026-11-03).
# usage: D=<serial> scripts/relic.py <account> [--dry] [--max-digs N]   (main screen, the Lost Continent map or the
#        board; ends on the main screen; --dry = read + plan only, no tap; exit 1 = stopped early, see v_relic.png)
#        scripts/relic.py --boards PNG...            offline: print each screenshot's board + plan (no device)
#        scripts/relic.py --learn PNG rN cM LABEL    add that cell as a tile exemplar (relic_tiles/LABEL.<n>.png) —
#                                                    only after looking at the cell; never from r6c1 (the % label)
# Reading: each of the 42 cells is matched against the exemplar crops in relic_tiles/ (nearest 24x24 thumb);
# no exemplar within THRESH -> '?' = never dug, never crossed (reported). Two consecutive reads must agree
# (reward banners / dig dust). Shovel counter and banners by OCR (flow.ocr).
# Planning (skill: "every dig needs a target"): Dijkstra over dig costs from the lit (diggable) cells; the item with
# the best value/cost >= RATIO is the target, its first path cell is dug; nothing worth it -> the cheapest bottom-row
# dig (reveals a new row). Boosters, One-Tap Mining, the shovel "+" are never tapped; the milestone reward is claimed.
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
         'shard': ('R', None), 'chest': ('C', None), 'gold': ('G', None), 'pick': ('P', None), 'multi': ('M', None)}
COST = {'D': 1, 'K': 1, 'S': 2, 'R': 1, 'C': 1, 'G': 1, 'P': 1, 'M': 1}
VALUE = {'R': 0.28, 'C': 1.0, 'M': 1.0, 'P': 0.14, 'G': 0.0}  # lv1-relic units (skill: shard lv1 .19 / lv2 .4, chest ~1)
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


def read(im):
    """7x6 grid of (kind, lit)."""
    return [[cell(im, r, c)[:2] for c in range(6)] for r in range(7)]


def show(g):
    """Text board: uppercase = lit (diggable now), lowercase = dark; '.' empty, '?' unknown."""
    return '\n'.join(' '.join(k if k in '.?' else (k if lit else k.lower()) for k, lit in row) for row in g)


def on_board(im): return all(max(abs(a - b) for a, b in zip(im.getpixel(p), c)) <= 12 for p, c in FRAME.items())


# ---------- planning ----------

def plan(g, blocked=()):
    """-> (r, c, why) for the next dig, or None. Dijkstra from the lit cells (cost = that cell's own dig cost) through
    diggable kinds; '?' and blocked cells are walls. Target = best value/cost >= RATIO; else cheapest bottom-row dig."""
    INF = 1e9
    def cost(r, c):
        k, lit = g[r][c]
        return INF if k in '.?' or (r, c) in blocked else COST[k]
    dist, prev, q = {}, {}, []
    for r in range(7):
        for c in range(6):
            if g[r][c][1] and cost(r, c) < INF:
                dist[(r, c)] = cost(r, c); prev[(r, c)] = None; heapq.heappush(q, (cost(r, c), r, c))
    while q:
        d, r, c = heapq.heappop(q)
        if d > dist.get((r, c), INF): continue
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < 7 and 0 <= nc < 6 and cost(nr, nc) < INF and d + cost(nr, nc) < dist.get((nr, nc), INF):
                dist[(nr, nc)] = d + cost(nr, nc); prev[(nr, nc)] = (r, c); heapq.heappush(q, (dist[(nr, nc)], nr, nc))
    def first(t):
        while prev[t] is not None: t = prev[t]
        return t
    name = {'R': 'shard', 'C': 'relic chest', 'M': 'multi chest', 'P': 'pickaxe'}
    worth = lambda r, c: g[r][c][0] in VALUE and VALUE[g[r][c][0]] > 0 and (r, c) not in blocked
    best = None
    for (r, c), d in dist.items():
        if not worth(r, c): continue
        # shared tunnel (Nick 2026-11-03: a gold chest is a fine stepping stone to 2+ shards): unlit items beside the
        # route become 1 dig each once it's dug -> they count toward this route's value and cost
        path, t = [], (r, c)
        while t is not None: path.append(t); t = prev[t]
        extra = {(nr, nc) for pr, pc in path for nr, nc in ((pr + 1, pc), (pr - 1, pc), (pr, pc + 1), (pr, pc - 1))
                 if 0 <= nr < 7 and 0 <= nc < 6 and (nr, nc) not in path and not g[nr][nc][1] and worth(nr, nc)}
        v = sum(VALUE.get(g[a][b][0], 0) for a, b in path) + sum(VALUE[g[a][b][0]] for a, b in extra)   # items on the way count too
        cst = d + sum(COST[g[a][b][0]] for a, b in extra)
        key = (v / cst, -cst, r)
        if v / cst >= RATIO - 1e-9 and (best is None or key > best[0]): best = (key, (r, c), d, len(extra), v / cst)
    if best:
        (r, c), d, n, ratio = best[1:]
        fr, fc = first((r, c))
        return fr, fc, f'route to {name[g[r][c][0]]} r{r + 1}c{c + 1}{f" +{n} beside it" if n else ""}, cost {d}, {ratio:.2f}/shovel'
    bottom = [(d, g[6][c][0] != 'D', abs(c - 2.5), c) for c in range(6) for d in [dist.get((6, c))] if d is not None]
    if not bottom: return None
    d, _, _, c = min(bottom)
    fr, fc = first((6, c))
    return fr, fc, f'dig down via r7c{c + 1}, cost {d}' if (fr, fc) != (6, c) else f'dig down r7c{c + 1}, cost {d}'


def booster_hint(g):
    """Where dynamite (diamond r=2) or the drill (column + bottom row) would collect the most items — logged only."""
    items = {(r, c) for r in range(7) for c in range(6) if g[r][c][0] in 'RCM'}
    if not items: return ''
    empties = [(r, c) for r in range(7) for c in range(6) if g[r][c][0] == '.']
    dyn = max(((sum(1 for (ir, ic) in items if abs(ir - r) + abs(ic - c) <= 2), r, c) for r, c in empties), default=(0, 0, 0))
    drl = max(((sum(1 for (ir, ic) in items if ic == c or ir == 6), r, c) for r, c in empties), default=(0, 0, 0))
    return f'booster hint (not used): dynamite r{dyn[1] + 1}c{dyn[2] + 1} -> {dyn[0]} items, drill r{drl[1] + 1}c{drl[2] + 1} -> {drl[0]} items'


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
    """Main screen / Lost Continent map / popup -> the dig board."""
    for _ in range(10):
        im = grab()
        if on_board(im): return
        boxes = ocr(im)
        if is_main(im): tap_wait(972, 1788); time.sleep(0.5); continue
        a = find(boxes, r'Archaeology')
        if a: tap_wait(*a); time.sleep(0.5); continue
        if find(boxes, r'Tap anywhere|Do not remind'): tap_wait(540, 120); continue
        time.sleep(1)
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
        p = plan(g); log(f'plan: {p and f"r{p[0] + 1}c{p[1] + 1} ({p[2]})"}'); log(booster_hint(g)); return 0
    digs, blocked, refused, got = 0, set(), 0, []
    cap = n[0] + 60 if max_digs is None else max_digs            # pickaxe refunds + regen add digs; 60 is a hard stop
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
        if dismiss(b2): b2 = ocr()
        if find(b2, r'adjacent plot'):
            blocked.add((r, c)); refused += 1; log(f'dig r{r + 1}c{c + 1} refused ("adjacent plot") -> blocked')
            if refused >= 3: raise Stop('3 refused digs')
            g, im = stable_board(); boxes = ocr(im); continue
        g2, im = stable_board()
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
    log(booster_hint(g))
    log(f'done: {digs} digs, shovels {n[0]}/{n[1]} left, items: {", ".join(got) or "none"}'
        + (f', UNKNOWN cells {unknown(g)}' if unknown(g) else '') + '\n' + show(g))
    if not leave(): raise Stop('not back on the main screen')
    return 0 if n[0] == 0 or (max_digs and digs >= max_digs) else 1


def learn(png, r, c, label):
    im = Image.open(png).convert('RGB'); r, c = int(r) - 1, int(c) - 1
    k = cell(im, r, c)
    n = len(glob.glob(os.path.join(TILES, label + '.*.png'))) + 1
    out = os.path.join(TILES, f'{label}.{n}.png')
    im.crop((X[c] - H, Y[r] - H, X[c] + H, Y[r] + H)).save(out)
    print(f'{out}: nearest before = {k[2]} ({k[3]:.1f})')


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['--learn']: learn(*a[1:5]); sys.exit()
    if a[:1] == ['--boards']:
        for f in a[1:]:
            im = Image.open(f).convert('RGB'); g = read(im); p = plan(g)
            print(f'{os.path.basename(f)}  board={on_board(im)}\n{show(g)}\nplan: {p and f"r{p[0] + 1}c{p[1] + 1} ({p[2]})"}\n')
        sys.exit()
    sys.path.insert(0, HERE)
    from tap import grab, tap as tap_wait
    from flow import Stop, find, joined, ocr, main
    ACCOUNT = a[0]; dry = '--dry' in a
    mx = int(a[a.index('--max-digs') + 1]) if '--max-digs' in a else None
    day = time.strftime('%F', time.gmtime(time.time() - 5 * 3600))
    LOG = None if os.environ.get('ACCOUNT') else os.path.join(HERE, '..', 'logs', ACCOUNT, day + '.log')  # daily.py tees itself
    if LOG: os.makedirs(os.path.dirname(LOG), exist_ok=True)
    main(run, ACCOUNT, dry, mx)
else:
    LOG = None
