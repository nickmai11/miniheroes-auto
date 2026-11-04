#!/usr/bin/env python3
# Offline check of relic.py (no device): the planner on the boards that went wrong by hand (Kong's stone shaft, Chien
# Than's board-mowing), and the tile reader on saved boards (relic_tiles/boards/*.png, crop y 510-1710 of a screenshot).
# usage: python3 scripts/test_relic.py
import os, sys
os.environ.setdefault('D', 'test')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
import relic
from relic import plan, read, show

def grid(s):
    """Text board (relic.show format: upper = lit, lower = dark, '.' empty, '?' unknown) -> grid."""
    return [[(ch.upper() if ch not in '.?' else ch, ch.isupper()) for ch in row.split()] for row in s.strip().splitlines()]

# Kong 2026-10-31: shard at r5c4 under stone r3c4 / dirt r4c4, lit dirt r5c3 beside it -> dig r5c3 (cost 1), not the shaft (3)
g = grid("""
. . . . . .
. . . . . .
. . . S . .
. . . d . .
. . D r . .
. . . d . .
. . . d . .""")
assert plan(g)[:2] == (4, 2), plan(g)
# Chien Than 2026-10-31: nothing to dig for -> never mow lit dirt in the top rows, go down the bottom row
g = grid("""
D D . . . .
d d . . . .
. . . . . .
. . . . . .
. . . . . .
. . . . . .
d d D S d d""")
assert plan(g)[:2] == (6, 2) and 'dig down' in plan(g)[2], plan(g)
# cheapest bottom-row dig: dirt (1) over stone (2), via the shaft
g = grid("""
. . . . . .
. . . . . .
. . . . . .
. . . . . .
. . . . . .
. . . D . .
d d S d d d""")
assert plan(g)[:2] == (5, 3), plan(g)          # the lit dirt above the bottom row (cost 1) then r7c4
# relic chest (1.6) worth up to ~11 digs, a shard only ~2
g = grid("""
. . . . . .
D d d d c .
. . . . . .
. . . . . .
. . . . . .
. . . . . .
d d D d d d""")
assert 'relic chest' in plan(g)[2] and plan(g)[:2] == (1, 0), plan(g)
g = grid("""
. . . . . .
D d d r . .
. . . . . .
. . . . . .
. . . . . .
. . . . . .
d d D d d d""")
assert 'dig down' in plan(g)[2], plan(g)       # shard at cost 4 (0.07/shovel) is not worth it
# unknown cells are walls; blocked cells are skipped; nothing left -> None
g = grid("""
. . . . . .
. . ? . . .
. . r . . .
. . . . . .
. . . . . .
. . . . . .
. . . . . .""")
assert plan(g) is None, plan(g)
g = grid("""
. . . . . .
. . . . . .
. . . . . .
. . . . . .
. . . . . .
. . . . . .
. . D . R .""")
assert plan(g)[:2] == (6, 4) and plan(g, blocked={(6, 4)})[:2] == (6, 2), (plan(g), plan(g, blocked={(6, 4)}))
# gold chest (Moon Essence) is never a target but can be tunnelled through
g = grid("""
. . . . . .
. . . . . .
. . . . . .
. . G . . .
. . c . . .
. . . . . .
. . . . . .""")
assert plan(g)[:2] == (3, 2) and 'relic chest' in plan(g)[2], plan(g)
# shared tunnel (Nick 2026-11-03): one shard 3 digs away through a gold chest isn't worth it, two of them are
g = grid("""
. . . . . .
. . . . . .
. . . D . .
. . . g . .
. . . r . .
. . . d . .
D d d d d d""")
assert 'dig down' in plan(g)[2], plan(g)
g = grid("""
. . . . . .
. . . . . .
. . . D . .
. . . g . .
. . . r . .
. . . r . .
D d d d d d""")
assert plan(g)[:2] == (2, 3) and 'shard' in plan(g)[2], plan(g)   # the 2nd shard is on the path or beside it
# Kong 2026-11-04 (Nick): a lit pickaxe is free and a bottom-row one reveals a row -> dig it before any route, even the
# relic chest (5 digs away here; the script dug 7 to it past the free pickaxe); blocked -> the chest route as before
g = grid("""
. . . . . .
. . . . . .
. . . . . .
. . . . . .
. . . . . .
g s s D . .
c d d d P d""")
assert plan(g)[:2] == (6, 4) and 'free pickaxe' in plan(g)[2], plan(g)
assert plan(g, blocked={(6, 4)})[:2] == (5, 3) and 'relic chest' in plan(g, blocked={(6, 4)})[2], plan(g, blocked={(6, 4)})
# a pickaxe on a route costs 0 (its shovel comes back): shard 2 net digs away is worth it (3 digs, 1 back)
g = grid("""
. . . . . .
. . . . . .
. . . . . .
. . . . . .
. . . . . .
. . . . . .
D p r . . .""")
assert plan(g)[:2] == (6, 0) and 'shard' in plan(g)[2], plan(g)
# Nick 2026-11-04: "dig down to see the path before choosing the hard way" — chest r7c1 behind 3 stones (7 digs): the
# hidden row below may hold a cheaper corridor from the lit dirt r7c5 -> dig down there first, then re-plan
g = grid("""
. . . . . .
. . . . . .
. . . . . .
S . . . . .
s . . . . .
s . . . . .
c s s s D .""")
assert plan(g)[:2] == (6, 4) and 'via the next row' in plan(g)[2], plan(g)
# ... the revealed row was all stone -> the known route it is (the hidden row below that can't lure it further down)
g = grid("""
. . . . . .
. . . . . .
S . . . . .
s . . . . .
s . . . . .
c s s s . .
s s s s S s""")
assert 'via' not in plan(g)[2] and 'cost 7' in plan(g)[2], plan(g)
# a reveal can't shorten a 3-dig route from above: no dig-down first
g = grid("""
. . . . . .
. . . . . .
. . . . . .
. . . . . .
. . . . . .
S . . . . .
c s s s D .""")
assert plan(g)[:2] == (5, 0) and 'via' not in plan(g)[2], plan(g)
# Nick 2026-11-04: a bottom-row dig scrolls row 1 off for good -> a worthwhile item up there is collected first,
# even before a free pickaxe; one not worth its route (shard 4 digs away) is let go and logged
g = grid("""
. R . . . .
. . . . . .
. . . . . .
. . . . . .
. . . . . .
. . . . . .
. . P . . .""")
assert plan(g)[:2] == (0, 1) and 'before the scroll' in plan(g)[2], plan(g)
g = grid("""
r d d D . .
. . . . . .
. . . . . .
. . . . . .
. . . . . .
. . . . . .
. . P . . .""")
assert plan(g)[:2] == (6, 2) and 'letting shard r1c1 (cost 4) go' in plan(g)[2], plan(g)
# boosters (mechanics verified 2026-11-04): shovels saved = hand-dig cost capped by the item's worth (chest ~7, shard 2,
# pickaxe 1): a stone-locked relic chest (7 by hand) + a lit shard two tiles away, in a diamond that touches the bottom
# row (+1, the row it reveals) = 9; the drill digs the bottom row only (nothing there -> 1); a worthwhile row-1 shard is
# lost by the scroll -> -1
g = grid("""
. . . . . .
. . . . . .
. . S . . .
. . s . . .
. . s . . .
R ? c ? . .
s s s s s s""")
c = relic.booster_plan(g)
assert c[0][1] == 'dynamite' and abs(c[0][0] - 9) < 0.01 and [x for x in c if x[1] == 'drill'][0][0] == 1, c[:3]
g[0][0] = ('R', True)
assert abs(relic.booster_plan(g)[0][0] - 8) < 0.01, relic.booster_plan(g)[:2]
# Kong 2026-11-04 (Nick): the gold chest r7c3 beside the dug r6c3 was read dark, so the 2 shards behind it looked 4+ digs
# away and a stone dig-down won; a tile beside a dug cell is diggable whatever its shade -> 3 digs for both shards
raw = grid("""
D D . . . .
. . . D . D
D . . D D D
. D . . D D
s g D . . D
g s . D D d
r r g s s s""")
assert 'dig down' in plan(raw)[2], plan(raw)
g = relic.light(raw)
assert g[6][2] == ('G', True) and plan(g)[:2] == (6, 2) and 'shard r7c2 +1 beside it' in plan(g)[2], plan(g)
# Bino 2026-11-03 (Nick): through a gold chest and a pickaxe tile to 2 shards = 4 digs (3 net) for ~0.7 units -> take it
g = grid("""
. . . . . .
. . . . . .
. . . . . .
. . . . . .
. . . . . .
D g p r . .
D d d r d d""")
assert plan(g)[:2] == (5, 0) and 'shard' in plan(g)[2], plan(g)   # same tunnel; named after r7c4 since the pickaxe is no item
# a shard on the way to a relic chest counts as well
g = grid("""
. . . . . .
. . . . . .
. . . . . .
. . . . . .
. . . . . .
. . R c . .
d d d d d d""")
assert plan(g)[:2] == (5, 2), plan(g)   # dig the shard first, the chest is credited either way
# cracked stone costs 1, whole stone 2
g = grid("""
. . . . . .
. . . . . .
. . . . . .
. . . . . .
. . . . . .
. . . . . .
S . . K . .""")
assert plan(g)[:2] == (6, 3), plan(g)

# tile reader: saved boards must read exactly as checked by eye (review sheets, 2026-11-03)
EXPECT = {
    'aminor_1030': """
. . . . . D
D . . . G d
d D . D d d
D . . . D r
s S S . D s
d d R . D s
d d s S p s""",
    'bino_1030': """
D . D r d d
. . D d d s
. S s s r s
. . S r d s
. D s s s d
. R d d g r
D c d p d d""",
    'chien_than_1030': """
. . . D S s
D D . . . D
s s S D . .
p s s s S .
d s d d D .
p s r p C .
s s d d r G""",
    'dino_1030': """
. . . . G d
D . D . . D
D . . . G d
D . S . D d
d S S . S p
g s R . S d
r d r G s d""",
    'chien_than_1031_cracked': """
. . . . . .
. . . . . .
S K . D . G
D . . D D d
p S . . D d
r D . D p d
s d S p g r""",
    'tiger_1103': """
s S . S s d
s D . S r d
d D . D d p
p D . D g d
p D . S g r
d R . D d r
d d D s d d""",
    'aminor_1104_multi': """
. . . . . D
. G D . G P
D G . . . .
d D M M S D
G . M M S d
d D . D r r
s s D d r d""",
    'aminor_1104_multi_pit': """
. G D . G .
D G . . . .
d D . . S D
G . . . S d
. . . . . R
S . . . . D
s D D S S s""",
    'cmajor_1104_multi6': """
S . D S D .
D . . . . .
. . D D D .
G S s S D .
d s D M M M
d p D M M M
d g d D D D""",
}
for name, want in EXPECT.items():
    im = Image.open(os.path.join(relic.TILES, 'boards', name + '.png')).convert('RGB')
    if im.size != (1080, 1920): full = Image.new('RGB', (1080, 1920)); full.paste(im, (0, 510)); im = full   # board crop (y 510-1710) or a full screenshot
    got = show(read(im))
    assert got == want.strip(), f'{name}:\n{got}\nwanted\n{want.strip()}'
assert relic.cell(Image.new('RGB', (1080, 1920), (0, 200, 0)), 0, 0)[0] == '?'   # a never-seen tile reads unknown
print('ok')

# planner (Chien Than 2026-11-04, Nick): of two 5-dig routes to a relic chest, the bottom row with 2 shards beats the
# column tunnel past 2 gold chests; and with 2 shovels left the lit shard is dug, not the first step of a 5-dig route.
_rows = ['. . . . . .', '. . . . . .', 'G . . . . .', 'd d d d . d', 'g d d d . d', 'd d d d . d', 'c d r d R d']
_g = [[(t.upper(), t.isupper()) if t != '.' else ('.', False) for t in r.split()] for r in _rows]
_p = relic.plan(_g); assert _p[:2] == (6, 4) and 'relic chest' in _p[2] and 'cost 5' in _p[2], _p
_p = relic.plan(_g, budget=2); assert _p[:2] == (6, 4) and 'shard' in _p[2], _p
print('planner ok')

# a lit multi chest opens for free (Cmajor 2026-11-04: shovels 1->1, Mine bar unchanged) -> dug before anything else
_rows = ['. . . . . .', '. . . . . .', '. . . . . .', 'G S s S D .', 'd s D M M M', 'd p D M M M', 'd g d D D D']
_g = [[(t.upper(), t.isupper()) if t != '.' else ('.', False) for t in r.split()] for r in _rows]
_p = relic.plan(_g); assert _p[:2] in {(r, c) for r in (4, 5) for c in (3, 4, 5)} and 'opens free' in _p[2], _p   # any tile of the chest
_p = relic.plan(_g, blocked={(4, 3), (4, 4), (4, 5), (5, 3), (5, 4), (5, 5)}); assert 'opens free' not in _p[2], _p   # a refused chest is left alone
print('multi chest ok')

# a multi chest outranks a relic chest (Nick 2026-11-04): a 3-dig route to an unlit multi chest beats the lit relic chest
# next to it (1 dig, better ratio); the chest is still collected after
_rows = ['. . . . . .', '. . . . . .', '. . . . . .', '. C . . . .', '. . . D . .', '. . . s m m', '. . . d m m']
_g = [[(t.upper(), t.isupper()) if t != '.' else ('.', False) for t in r.split()] for r in _rows]
_p = relic.plan(_g); assert _p[:2] == (4, 3) and 'multi chest' in _p[2] and 'cost 3' in _p[2], _p
_p = relic.plan(_g, budget=2); assert _p[:2] == (3, 1) and 'relic chest' in _p[2], _p   # can't afford the 3 digs -> the chest
print('multi first ok')
