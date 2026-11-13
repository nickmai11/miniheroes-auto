#!/usr/bin/env python3
# Upgrade the divinities (6 badges around the artifact, Hero -> Artifact) of every hero after the first N to the
# levels in accounts/divinities.yaml (Nick, Kratos 2026-11-12). usage: D=<serial> scripts/divinity.py [--keep 6]
# [--here] (main or hero screen; --here = resume at the selected hero after a stop). Only listed names with a value
# are touched (Nick: "shouldn't upgrade what not listed" - Basic/Intermediate HP/ATK aren't). Crystals (one kind per
# badge colour) + gold only, never gems.
# Per badge: Enhance once -> "↑ Lv.N" quick button (next multiple of 50) -> Quick Level Up dialog Lv.a -> Lv.b,
# Confirm only if b <= target; single Enhance taps for the rest. Every step is read back from the popup.
import os, re, sys
from flow import Stop, find, main, ocr, tap_wait, wait
import hero as hero_mod
import rebirth_level as rl

CFG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'accounts', 'divinities.yaml')
SLOTS = [('purple', 184, 380), ('purple', 896, 380), ('gold', 120, 580), ('gold', 960, 580),
         ('red', 184, 784), ('red', 896, 784)]
LVROW, NAME, QUICK = (560, 790, 940, 850), (330, 850, 600, 905), (380, 980, 720, 1060)
ENHANCE, CONFIRM, CLOSE, ARTI = (540, 1166), (740, 1160), (540, 120), (920, 1300)


def load(text):
    """{colour: {name: level}} from 'colour:' sections and '  name: units' lines (blank = not listed); 1 unit = 50."""
    cfg, sec = {}, None
    for line in text.splitlines():
        m = re.match(r'^(\w+):', line)
        if m: sec = cfg.setdefault(m[1], {}); continue
        m = re.match(r'^\s+([^#:]+?):\s*(\d+)', line)
        if m and sec is not None: sec[m[1]] = int(m[2]) * 50
    return cfg


def key(colour, name, names=()):
    """Config name of a popup stat. OCR junk seen on Kratos 2026-11-12: 'AIl'/'AlI' for All, a trailing ' |', values
    glued on ('Marksman ATK 1140'), long names cut ('All Melee DMG Reduct') -> the one listed name starting with it.
    Red names are stored without the popup's 'All '; purple/gold keep it."""
    name = re.sub(r'^A[lI1]{2}\b', 'All', re.sub(r'(\s*[\d.,]+%?|[\s|]+)$', '', name.strip()))
    if colour == 'red': name = re.sub(r'^All\s+', '', name)
    cut = [c for c in names if c.startswith(name) and len(name) >= 10]
    return name if name in names or len(cut) != 1 else cut[0]


def popup():
    """(name, level) of the open badge popup. Level 0 doesn't OCR, so the next level (right column) - 1 when present."""
    b = wait(r'Divinity$', 5)
    nums = sorted((x, int(t)) for x, y, w, h, t in b
                  if t.isdigit() and LVROW[0] <= x + w // 2 <= LVROW[2] and LVROW[1] <= y + h // 2 <= LVROW[3])
    name = next((t for x, y, w, h, t in b if NAME[0] <= x <= 500 and NAME[1] <= y + h // 2 <= NAME[3]), '')
    if not nums or not name: raise Stop(f'popup not readable: {nums} {name!r}')
    lv = nums[-1][1] - 1 if nums[-1][0] > 780 else nums[-1][1]
    return name, lv


def level(old):
    """Level once it moved off old and 2 reads agree: the popup redraws ~1 s after a tap (read 1 after a quick to 50,
    Wine Immortal). Still old after ~8 s -> old (the caller stops: out of crystals/gold)."""
    prev = None
    for _ in range(16):
        try: v = popup()[1]
        except Stop: v = None
        if v is not None and v != old and v == prev: return v
        prev = v
    if prev == old: return old
    raise Stop('level not readable')


class Empty(Exception): pass


def short(n, colour, name, lv, new):
    """Enhance did nothing: the cost row 'have/need' (crystals left, gold right) says why. Crystals short -> Empty
    (that colour is done for the run, Kratos ran out of red at Dark Shaman 2026-11-12); gold short or neither -> Stop."""
    cost = {x < 540: hero_mod.num(m[1]) < hero_mod.num(m[2]) for x, y, w, h, t in ocr() if 980 <= y + h // 2 <= 1040
            for m in [re.search(r'([\d.]+[kKmM]?)\s*/\s*([\d.]+[kKmM]?)', t)] if m}
    if cost.get(True): raise Empty(f'{n}: {colour} {name} stuck at {lv}: out of {colour} crystals')
    raise Stop(f'{n} {name}: Enhance {lv} -> {new}' + (' (out of gold)' if cost.get(False) else ''))


def upgrade(n, colour, name, lv, target):
    start = lv
    while lv < target:
        b = ocr(); q = find(b, r'L[Vv]\.?\s*\d+', QUICK)
        if q and lv % 50:
            btn = [t for x, y, w, h, t in b if QUICK[1] <= y + h // 2 <= QUICK[3] and re.search(r'L[Vv]', t)]
            tap_wait(*q); d = wait(r'Quick Level Up', 5)
            # button "↑ Lv.N" + the dialog's "Lv.a -> Lv.b" line only (the cards behind OCR as 'Lv.18x'; the green
            # 'Lv.150' sometimes doesn't OCR at all) -> the highest number = where it goes
            line = [t for x, y, w, h, t in d if 780 <= y <= 900]
            to = max(int(v) for t in btn + line for v in re.findall(r'\d+', t))
            if to > target: tap_wait(336, 1160); raise Stop(f'{n} {name}: quick goes to {to} > {target}')  # Cancel
            tap_wait(*CONFIRM); wait(r'Divinity$', 5); new = level(lv)
            if new != to: raise Stop(f'{n} {name}: quick {lv} -> {new}, expected {to}')
        else:
            tap_wait(*ENHANCE); new = level(lv)
            if new != lv + 1: short(n, colour, name, lv, new)
        lv = new
    print(f'{n}: {colour} {name} {start} -> {lv}', flush=True)


SKIP = {'Bone Archer'}   # the dailies hero (rebirthed every day) - never touched (Nick 2026-11-12)


def hero(n, cfg, empty):
    """All 6 badges of the selected hero, each to its target, on the Artifact tab (no tab switching, Nick 2026-11-12).
    Colours in `empty` (out of crystals) are skipped."""
    if n in SKIP: print(f'{n}: excluded', flush=True); return
    for colour, x, y in SLOTS:
        if colour in empty: continue
        tap_wait(x, y)
        try: wait(r'Divinity$', 2)
        except Stop: print(f'{n}: {colour} badge locked', flush=True); continue   # padlock / "Lv.100" (Bone Archer)
        name, lv = popup(); k = key(colour, name, cfg.get(colour, {}))
        target = cfg.get(colour, {}).get(k)
        if target is None: print(f'{n}: {colour} {name} Lv.{lv} not listed', flush=True)
        elif lv >= target: print(f'{n}: {colour} {name} Lv.{lv} >= {target}', flush=True)
        else:
            try: upgrade(n, colour, k, lv, target)
            except Empty as e: empty.add(colour); print(f'{e} -> no more {colour} upgrades this run', flush=True)
        tap_wait(*CLOSE); wait(r'Ascension', 5)


def next_hero():
    """The card right after the selected one (the Artifact tab stays open); None at the row end."""
    for _ in range(6):
        x = rl.selected()[1] + 105
        if x <= 1000: tap_wait(x, rl.Y); return hero_mod.name(wait(r'Ascension', 6))
        if not rl.drag(-rl.STEP): return None
    raise Stop('next card not reachable')


def first_after(keep):
    """Row start (slow drags), card 1 (lower half: the Quick Ascend badge covers its top), then `keep` cards on."""
    while rl.drag(rl.STEP): pass
    tap_wait(96, 1650); names = [hero_mod.name(wait(r'Ascension', 6))]
    for _ in range(keep):
        n = next_hero()
        if not n or n in names: raise Stop(f'row shorter than {keep + 1} heroes: {names}')
        names.append(n)
    print(f'first {keep} kept: {names[:keep]}', flush=True)
    return names[-1]


def run(keep=6, here=False):
    """here: resume at the selected hero (after a stop) instead of walking the row from card 1 again (Nick 2026-11-12)."""
    cfg = load(open(CFG).read())
    b = ocr()
    if find(b, r'Quick Level Up'): tap_wait(336, 1160); b = wait(r'Divinity$', 5)   # left open by a stop: Cancel
    if find(b, r'Divinity$'): tap_wait(*CLOSE); b = wait(r'Ascension', 5)
    if not find(b, r'Ascension|^Level Up$'): tap_wait(274, 1810); b = wait(r'Ascension|^Level Up$', 10)  # main -> Hero
    if not find(b, r'Ascension'): tap_wait(*ARTI); b = wait(r'Ascension', 6)
    n, done, empty = hero_mod.name(b) if here else first_after(keep), 0, set()
    while n and len(empty) < 3:
        hero(n, cfg, empty); done += 1; n = next_hero()
    print(f'{"row end" if not n else "all crystals out"}: {done} heroes done' + (f', out of {sorted(empty)}' if empty else ''))


if __name__ == '__main__':
    if sys.argv[1:] == ['test']:
        c = load('red:\n  # ATK\n  ATK: 1\n  HP:\npurple: # 3 for all\n  Warrior HP: 3\n')
        assert c == {'red': {'ATK': 50}, 'purple': {'Warrior HP': 150}}, c
        assert key('red', 'AIl CRIT DMG Reduction') == 'CRIT DMG Reduction'
        assert key('red', 'All Physical DMG Boost 1.00%') == 'Physical DMG Boost'
        assert key('gold', 'Marksman ATK 1140') == 'Marksman ATK' and key('gold', 'All HP') == 'All HP'
        cfg = load(open(CFG).read())
        assert key('gold', 'AlI ATK', cfg['gold']) == 'All ATK'
        assert key('red', 'All Knockback Effect |', cfg['red']) == 'Knockback Effect'
        assert key('red', 'All Melee DMG Reduct', cfg['red']) == 'Melee DMG Reduction'
        assert key('red', 'All Heavy Injury 1.50%', cfg['red']) == 'Heavy Injury'
        assert load(open(CFG).read())['purple']['Warrior HP'] == 150
        print('ok'); sys.exit()
    a = sys.argv[1:]
    main(run, int(a[a.index('--keep') + 1]) if '--keep' in a else 6, '--here' in a)
