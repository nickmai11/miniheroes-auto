#!/usr/bin/env python3
# Hero faces: learn each hero's avatar from the expanded hero list, then name cards by face (Nick 2026-11-14).
# usage: D=<serial> scripts/hero_faces.py learn [--all]   main screen -> Hero -> expanded list (All) -> each card whose face
#            isn't recognised: tap, read the name top-left, save scripts/heroes/<name>.png; ends on the hero screen.
#            --all: tap every card and count MISREADs (ident vs the name) - the check after any matching change
#        D=<serial> scripts/hero_faces.py who       expanded list open -> "x y name score best-other" per full card
# Skins change the avatar (Nick 2026-11-14): a face that matches no saved one is saved as <name>_2.png, _3 ... so every
# skin seen on any account is kept. learn is view-only (taps cards, never a button).
import fcntl, os, re, subprocess, sys, time
import numpy as np
from PIL import Image
from flow import D, grab, ocr, swipe, tap_wait

import hero

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'heroes')
COLS = (140, 336, 536, 734, 932)                     # card centres x; cards 168 wide, 210 tall, rows ~236 apart
TOP, BOTTOM = 1130, 1716                             # list area above the class filter bar (last row ends ~1710)
BG = np.array([189, 190, 197])                       # grey between rows
SAME = 22                                            # gray diff: same face <16, closest 2 heroes 28.4 (Cmajor 11-14)


def rows(im, bg=BG):
    """Top y of every card row fully on screen: a run of card lines 213-221 px long (cards are 217) between grey gaps,
    measured on each card's left part: red dots / class badges stick out ~12 px above the top right and put every
    face of such a row 12 px off (pawn2 11-14), a card cut by the list's edges makes a shorter run."""
    a = np.asarray(im.convert('RGB'), dtype=int)
    cols = np.concatenate([np.arange(x - 80, x + 30) for x in COLS])
    card = [(np.abs(a[y, cols] - bg).sum(1) >= 30).mean() >= 0.1 for y in range(TOP, BOTTOM)] + [False]
    out, start = [], None
    for i, c in enumerate(card):
        if c and start is None: start = i
        if not c and start is not None:
            if start > 0 and 213 <= i - start <= 221: out.append(TOP + start)
            start = None
    return out


def face(im, x, top):
    """Card art between the Lv label (ends top+36) and the stars (top+180), left of the setup's gear icons (x+44..)."""
    return im.crop((x - 80, top + 40, x + 42, top + 176)).convert('L')


def diff(a, b):
    """Mean abs gray diff at 1/4 scale, best of +-8 px shifts (row tops are read to a few px)."""
    a = np.asarray(a.reduce(4), dtype=np.float32); b = np.asarray(b.reduce(4), dtype=np.float32)
    return min(np.abs(np.roll(a, (dy, dx), (0, 1)) - b)[2:-2, 2:-2].mean() for dy in (-2, -1, 0, 1, 2) for dx in (-1, 0, 1))


def known():
    os.makedirs(DIR, exist_ok=True)
    return {f[:-4]: Image.open(os.path.join(DIR, f)).convert('L') for f in sorted(os.listdir(DIR)) if f.endswith('.png')}


# Battle setup cards are darkened and carry a green check / padlock over the face centre (Cmajor 11-14: plain diff 1/10
# right) -> normalised correlation outside that box: 10/10, right hero 0.64-0.87, best other hero <= 0.47.
MASK = np.zeros((136, 122), bool); MASK[6:-6, 6:-6] = True; MASK[18:126, 38:116] = False   # check / padlock box
OK, LEAD = 0.55, 0.15
SURE = 0.75   # learn trusts a match only from here: known faces in the list read >= 0.83 (Cmajor/Kong 11-14), other
              # heroes <= 0.56 -> a new skin that looks like another hero lands between and gets tapped + learnt


def _norm(v): v = v - v.mean(axis=-1, keepdims=True); return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-6)


_T = None


def ident(f):
    """Face crop (any card: list or battle setup) -> (name or '' if unsure, score, best other hero's score)."""
    global _T
    if _T is None:
        k = known()
        if not k: return '', 0.0, 0.0
        _T = ([re.sub(r'_\d+$', '', n) for n in k], _norm(np.stack([np.asarray(v, np.float64)[MASK] for v in k.values()])))
    names, t = _T; a = np.asarray(f, np.float64)
    shifts = _norm(np.stack([np.roll(a, (dy, dx), (0, 1))[MASK] for dy in range(-10, 11, 2) for dx in range(-4, 5, 2)]))   # climb's scroll offset drifts
    with np.errstate(all='ignore'): sc = (t @ shifts.T).max(axis=1)   # numpy 2 + macOS Accelerate: spurious matmul warnings
    i = int(sc.argmax())
    other = max((s for n, s in zip(names, sc) if n != names[i]), default=0)
    return (names[i] if sc[i] >= OK and sc[i] - other >= LEAD else ''), round(float(sc[i]), 2), round(float(other), 2)


def cards(im):
    return [(x, top + 110, face(im, x, top)) for top in rows(im) for x in COLS
            if (np.abs(np.asarray(im.convert('RGB'))[top + 110, x - 90:x + 90] - BG).sum(1) >= 30).mean() > 0.5]


def still():
    a = grab()
    for _ in range(30):                                               # glides 3 s+ after a slow swipe (Cmajor 11-14)
        time.sleep(0.3); b = grab()
        if rows(a) == rows(b) and diff(a.crop((0, TOP, 1080, BOTTOM)).convert('L'), b.crop((0, TOP, 1080, BOTTOM)).convert('L')) < 1: return b
        a = b
    return a


def scroll(y0, y1):
    """Slow swipe, wait till still -> (moved, screen)."""
    a = grab().crop((0, TOP, 1080, BOTTOM)).convert('L')
    swipe(540, y0, 540, y1, 1500)
    b = still(); return diff(a, b.crop((0, TOP, 1080, BOTTOM)).convert('L')) >= 2, b


def learn():
    global _T
    seen, prev, bad = [], '', 0
    tap_wait(274, 1810)                                               # Hero (from the main screen)
    if not re.search(r'Level Up|Attribute', ' '.join(t for *_, t in ocr())):   # Cmajor 11-14: started off the main screen,
        sys.exit('not on the Hero screen after the Hero tap - stopped')        # its taps hit the Relic screen
    tap_wait(1008, 1400); tap_wait(284, 1800)                         # expand list -> All
    for _ in range(30):                                               # the game keeps the list's scroll spot: to the top
        if not scroll(1350, 1700)[0]: break
    for _ in range(80):
        im = still()
        for x, y, f in cards(im):
            if any(diff(f, s) < SAME for s in seen): continue          # same card, seen before this scroll
            seen.append(f)
            n0, s0, _ = ident(f)
            if '--all' not in sys.argv and n0 and s0 >= SURE: continue  # sure: no tap (--all: tap all, count misreads)
            tap_wait(x, y)
            for _ in range(10):                                       # name top-left updates after the tap
                n = hero.name(ocr()).strip()
                if n and n != prev: break
                time.sleep(0.3)
            else: print(f'{x},{y}: name unchanged ({n!r}) - skipped'); continue
            prev = n; n = re.sub(r'(?<=[a-z])[A-Z]$', '', n)              # 'HelaR': a badge glyph read into the name
            slug = re.sub(r'\W+', '_', n.lower()).strip('_')
            with open(os.path.join(DIR, '.lock'), 'w') as lk:          # learn runs on many accounts at once
                fcntl.flock(lk, fcntl.LOCK_EX); _T = None
                got = ident(f)
                if got[0] == slug and got[1] >= SURE: continue
                if got[0] and got[0] != slug: bad += 1; print(f'MISREAD {n} as {got[0]} {got[1:]}')
                mine = [k for k in known() if re.sub(r'_\d+$', '', k) == slug]
                k = slug if not mine else f'{slug}_{len(mine) + 1}'
                f.save(os.path.join(DIR, k + '.png')); _T = None
                print(f'{n}: saved {k}.png' + (f' (new skin / closer variant; read {got})' if mine else ''))
        page = [f for _, _, f in cards(im)]
        moved, im = scroll(1600, 1350)                                # slow, no fling - but it still glides 30-400 px
        if not moved: break                                           # list end
        for _ in range(6):                                            # glided past a row: no face of the last page left
            if any(diff(f, p) < SAME for _, _, f in cards(im) for p in page): break
            moved, im = scroll(1400, 1500)
        else: print('lost my place in the list - stopped'); break
    tap_wait(1008, 1100)                                              # close the list
    print(f'{len(seen)} cards, {bad} misread, {len(known())} faces in {DIR}')


def who():
    for x, y, f in cards(still()): print(x, y, *ident(f))


if __name__ == '__main__':
    {'learn': learn, 'who': who}[sys.argv[1]]()
