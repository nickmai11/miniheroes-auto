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
# relic chest worth up to ~7 digs, a shard only ~2
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
# Bino 2026-11-03 (Nick): through a gold chest and a pickaxe tile to 2 shards = 4 digs for ~0.7 units -> take it
g = grid("""
. . . . . .
. . . . . .
. . . . . .
. . . . . .
. . . . . .
D g p r . .
D d d r d d""")
assert plan(g)[:2] == (5, 0) and 'shard r6c4 +1 beside it' in plan(g)[2], plan(g)
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
}
for name, want in EXPECT.items():
    im = Image.new('RGB', (1080, 1920)); im.paste(Image.open(os.path.join(relic.TILES, 'boards', name + '.png')), (0, 510))
    got = show(read(im))
    assert got == want.strip(), f'{name}:\n{got}\nwanted\n{want.strip()}'
assert relic.cell(Image.new('RGB', (1080, 1920), (0, 200, 0)), 0, 0)[0] == '?'   # a never-seen tile reads unknown
print('ok')
