#!/usr/bin/env python3
"""Relic dig: print the board as text so no screenshot has to be read.

usage: D=<serial> relic.py [R,C]      optionally dig cell R,C (row 0-6 top->bottom, col 0-5), then print the board
       D=<serial> relic.py --learn N  label the '?' counter digit(s) from the last run (see c.png) as N
       --debug                        also print per-cell features
legend (uppercase = touches an empty cell, so diggable now; lowercase = not yet):
  .  empty     D/d dirt (1 hit)     S/s stone (2 hits)     R/r relic shard     P/p shovel (free)
  M/m multi-square chest (must get)  G/g gold chest (ignore)           ?  unknown item (relic chest, multi-square chest, popup) -> look at r.png
Writes r.png (540 wide) every run, for when a '?' or 'UNEXPECTED' needs eyes.
"""
import json, os, subprocess, sys, time
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from tap import grab, tap  # noqa: E402

X = [116, 284, 452, 624, 794, 962]
Y = [600, 770, 940, 1110, 1280, 1450, 1620]
ITEM = (107, 85, 66)  # corner colour of an item's dug-hole tile (unlit)
ITEM_LIT = (181, 150, 115)
MULTI = (37, 24, 4)  # corner colour inside a multi-square chest
BG = {'.': (58, 49, 49), 'D': (172, 140, 106), 'd': (98, 80, 57), 'S': (139, 129, 138), 's': (80, 73, 74)}
DIGITS = os.path.join(os.path.dirname(__file__), 'relic_digits.json')
PENDING = '/tmp/relic_pending_glyphs.json'


def nearest(col, opts):
    return min(((k, np.abs(col - v).sum()) for k, v in opts.items()), key=lambda t: t[1])


def cell(a, r, c, debug):
    """-> (char, corner_ok). Plain tiles are judged by the centre's dominant colour (robust to the % label),
    items by the item-hole corner colour + icon colours."""
    x, y = X[c], Y[r]
    corner = np.median(a[y - 68:y - 62, x + 62:x + 68].reshape(-1, 3), 0)
    ck, cd = nearest(corner, {**BG, 'I': ITEM, 'I2': ITEM_LIT})
    reg = a[y - 45:y + 45, x - 45:x + 45].reshape(-1, 3)
    med = np.median(reg, 0)
    plain = (np.abs(reg - med).sum(1) < 30).mean()
    R, G, B = reg[:, 0], reg[:, 1], reg[:, 2]
    blue = ((B > R + 40) & (B > G + 5)).mean()
    purple = ((B > G + 30) & (R > G + 15)).mean()
    k, d = nearest(med, BG)
    if debug:
        print(f'  {r},{c} corner={corner.astype(int)} {ck}~{cd:.0f} med={med.astype(int)} {k}~{d:.0f} plain={plain:.2f} blue={blue:.2f} purple={purple:.3f}')
    if not (ck in ('I', 'I2') and cd <= 10) and plain > 0.6 and d <= 25:
        v = k
    elif ck in ('S', 's') and cd <= 15 and blue < 0.02:
        v = 'S'  # cracked stone
    elif blue > 0.18:
        v = 'R'
    elif purple > 0.005 and blue > 0.03:
        v = 'G'
    elif blue < 0.1 and purple < 0.005 and ck in ('I', 'I2') and cd <= 10:  # lit blade looks a bit blue
        v = 'P'
    elif nearest(corner, {'M': MULTI})[1] <= 15:
        v = 'M'
    else:
        v = '?'
    return v.upper(), cd <= 30


def glyphs(a):
    w = a[380:430, 80:260].min(2) > 200
    cols, out, start = list(w.any(0)) + [False], [], None
    for i, on in enumerate(cols):
        if on and start is None:
            start = i
        elif not on and start is not None:
            g = w[:, start:i]
            rows = np.where(g.any(1))[0]
            g = Image.fromarray((g[rows.min():rows.max() + 1] * 255).astype(np.uint8)).resize((8, 12))
            out.append(''.join('1' if v > 127 else '0' for v in np.asarray(g).flatten()))
            start = None
    return out[:-4]  # drop the fixed "/150"


def shovels(a):
    known = json.load(open(DIGITS)) if os.path.exists(DIGITS) else {}
    gs, s, unknown = glyphs(a), '', []
    for g in gs:
        best = min(known.items(), key=lambda kv: sum(p != q for p, q in zip(kv[0], g)), default=None)
        if best and sum(p != q for p, q in zip(best[0], g)) <= 8:
            s += best[1]
        else:
            s += '?'; unknown.append(g)
    if unknown:
        json.dump(unknown, open(PENDING, 'w'))
        Image.fromarray(a[370:440, 20:320].astype(np.uint8)).save('c.png')
        print('unknown counter digit(s): look at c.png, then relic.py --learn <the digits shown as ?>')
    return s


def read(a):
    return [[cell(a, r, c, False)[0] for c in range(6)] for r in range(7)]


def on_board(a):
    return sum(cell(a, r, c, False)[1] for r in range(7) for c in range(6)) >= 34


def board(debug=False):
    for _ in range(8):  # reward banners/fading pieces -> wait until two reads agree
        a = np.asarray(grab()).astype(int)
        g = read(a)
        time.sleep(0.4)
        b = np.asarray(grab()).astype(int)
        if g == read(b):
            break
    if debug:
        [cell(b, r, c, True) for r in range(7) for c in range(6)]
    Image.fromarray(b.astype(np.uint8)).resize((540, 960)).save('r.png')
    lines = []
    for r in range(7):
        row = ''
        for c in range(6):
            v = g[r][c]
            open_ = any(0 <= r + dr < 7 and 0 <= c + dc < 6 and g[r + dr][c + dc] == '.'
                        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            row += v if v in '.?' else (v.upper() if open_ else v.lower())
        lines.append(f'{r} {" ".join(row)}')
    print('  0 1 2 3 4 5'); print('\n'.join(lines))
    print('shovels', shovels(b))
    if not on_board(b):
        print('UNEXPECTED: not the Relic board - check r.png')


def main(argv):
    debug = '--debug' in argv
    argv = [x for x in argv if x != '--debug']
    if argv[:1] == ['--learn']:
        known = json.load(open(DIGITS)) if os.path.exists(DIGITS) else {}
        for g, d in zip(json.load(open(PENDING)), argv[1]):
            known[g] = d
        json.dump(known, open(DIGITS, 'w'), indent=0); print('learned', argv[1]); return
    if argv:
        r, c = map(int, argv[0].split(','))
        if not on_board(np.asarray(grab()).astype(int)):
            print('UNEXPECTED: not the Relic board - tap refused'); board(debug); sys.exit(1)
        tap(X[c], Y[r])
    board(debug)


if __name__ == '__main__':
    main(sys.argv[1:])
