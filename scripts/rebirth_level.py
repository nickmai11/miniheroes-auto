#!/usr/bin/env python3
# Rebirth every hero after the first N (hero list order) and level them back to a target (Nick, Kratos 2026-11-12).
# usage: D=<serial> scripts/rebirth_level.py <account> [--keep 6] [--target 160] [--phase both|rebirth|level]
#        (main screen or hero screen). Potions only: Rebirth is free and returns 100% of the hero AND gear materials
#        (the gear goes back to LV.0 too). The account's dailies hero (hero_upgrade.hero, e.g. Bone Archer) is left alone:
#        hero.py rebirths it above Lv.135 every day anyway.
# Works on the hero screen's bottom row (list order). Strict order, no OCR of the row: the selected card is the only one
# reaching up into y=1445; the next hero = the card right after it; off-screen -> one slow 2-card drag (Nick: scroll
# slowly, never fling). Phase rebirth first (all refunds pooled), then level: Lv.1 -> quick Lv.90 -> held Level Up ->
# single taps for the last <= 4 levels. A hero found above the target is rebirthed and redone.
import os, re, subprocess, sys, time
import hero
from flow import Stop, D, find, grab, main, ocr, tap_wait, wait

BTN, LV = (200, 1050, 880, 1300), (300, 340, 800, 460)
ROW, Y, STEP = (0, 1480, 1080, 1700), 1600, 382       # bottom hero row; cards ~191 px apart; one drag = 2 cards


def lv_now():
    """Hero level from the header, 2 equal reads in a row (the label redraws digit by digit)."""
    prev = None
    for _ in range(10):
        v = hero.level(ocr(), LV)
        if v is not None and v == prev: return v
        prev = v; time.sleep(0.6)
    raise Stop('hero level not readable')


def hold(sec):
    p = find(wait(r'^Level Up$', 6, BTN), r'^Level Up$', BTN)
    subprocess.run(['adb', '-s', D, 'shell', 'input', 'swipe', *map(str, (p[0], p[1], p[0], p[1], int(sec * 1000)))])
    time.sleep(1.2)


def to_level(target):
    """Held Level Up runs ~1.0-1.6 levels/s (8 s: +8..13, 52 s: +68, Kratos): each hold sized at 2/s to stop short of
    target-4 (max 30 s), then single taps, each read back. Rapid taps don't stack (10 taps = +1)."""
    lv = lv_now()
    while target - lv > 4:
        hold(min(30, max(0.5, (target - 4 - lv) / 2))); lv2 = lv_now()
        if lv2 <= lv: raise Stop(f'hold did not level ({lv} -> {lv2}), potions {hero.potions(ocr())}')
        lv = lv2
    while lv < target:
        tap_wait(*find(wait(r'^Level Up$', 6, BTN), r'^Level Up$', BTN)); lv2 = lv_now()
        if lv2 != lv + 1: raise Stop(f'{lv} -> {lv2} after one Level Up')
        lv = lv2
    return lv


def rebirth(n, lv):
    """Rebirth icon above its label -> Rebirth Preview (free, '100%' returned) -> Confirm -> Congratulations -> Lv.1."""
    r = find(ocr(), r'^Rebirth$')
    if not r: raise Stop(f'{n}: no Rebirth button')
    tap_wait(r[0], r[1] - 40); b = wait(r'Rebirth Preview', 5)
    if not find(b, r'100%'): raise Stop(f'{n}: Rebirth Preview without the 100% line')
    hero.confirm('Rebirth Preview'); wait(r'Congratulations', 6); tap_wait(540, 120); wait(r'^Level Up$', 6, BTN)
    print(f'{n}: Lv.{lv} -> Rebirth', flush=True)


def level_up(n, lv, target):
    if lv > target: rebirth(n, lv); lv = 1
    if lv < 90: hero.quick_90(n)                       # "↑ Lv.N" quick button goes to the TOP level (185), not usable above 90
    r = to_level(target)
    if r > target: rebirth(n, r); hero.quick_90(n); r = to_level(target)
    print(f'{n}: Lv.{lv} -> Lv.{r}', flush=True)


def still():
    return list(hero.settle(ROW).crop(ROW).get_flattened_data())[::97]


def drag(dx):
    """Slow held drag only (Nick 2026-11-12), then wait until the row is still. True = the row moved."""
    a = still()
    subprocess.run(['adb', '-s', D, 'shell', 'input', 'swipe', *map(str, (540 - dx // 2, Y, 540 + dx // 2, Y, 1500))])
    return not hero.same(still(), a)


def selected():
    """(left, right) x of the selected card: the only card reaching up into y=1445, where the row background is a flat
    192 grey. First run of non-grey pixels (its badge gap merged); x >= 960 = the list icon."""
    im = grab(); runs = []
    for x in range(0, 960, 4):
        if abs(sum(im.getpixel((x, 1445))[:3]) / 3 - 192) > 8:
            if runs and x - runs[-1][1] <= 24: runs[-1][1] = x
            else: runs.append([x, x])
    if not runs: raise Stop('no selected card in the row')
    return tuple(runs[0])


def pick(x):
    tap_wait(x, Y); time.sleep(0.3); b = ocr()
    return hero.name(b), hero.level(b, LV) or lv_now()


def next_hero():
    """The card right after the selected one; None at the end of the row (a drag that doesn't move it)."""
    for _ in range(6):
        x = selected()[1] + 105                        # selected card's right edge + ~105 = next card's centre
        if x <= 1000: return pick(x)
        if not drag(-STEP): return None
    raise Stop('next card not reachable')


def first_after(keep):
    """Row start (slow drags until it stops), card 1 (under the Quick Ascend badge: tap its lower half), then `keep` steps."""
    while drag(STEP): pass
    tap_wait(96, 1650); time.sleep(0.3); names = [hero.name(ocr())]
    for _ in range(keep):
        h = next_hero()
        if not h or h[0] in names: raise Stop(f'row shorter than {keep + 1} heroes: {names}')
        names.append(h[0])
    print(f'first {keep} kept: {names[:keep]}', flush=True)
    return names[-1], lv_now()


def walk(keep, act):
    n, lv = first_after(keep); seen = 0
    while True:
        act(n, lv); seen += 1
        h = next_hero()
        if not h: print(f'row end: {seen} heroes after the first {keep}, last {n}', flush=True); return
        n, lv = h


def run(account, keep=6, target=160, phase='both'):
    cfg = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'accounts', account + '.yaml')).read()
    skip = {m.strip() for m in re.findall(r'hero_upgrade:\s*\n\s+hero:\s*(.+)', cfg)}
    if not find(ocr(), r'^Level Up$', BTN): tap_wait(274, 1810); wait(r'^Level Up$', 10, BTN)   # main -> Hero
    if phase in ('both', 'rebirth'):
        walk(keep, lambda n, lv: None if n in skip or lv == 1 else rebirth(n, lv))
    if phase in ('both', 'level'):
        walk(keep, lambda n, lv: None if n in skip or lv == target else level_up(n, lv, target))
    print('rebirth/level done')


if __name__ == '__main__':
    a = sys.argv[1:]
    opt = lambda k, d: type(d)(a[a.index(k) + 1]) if k in a else d
    main(run, a[0], opt('--keep', 6), opt('--target', 160), opt('--phase', 'both'))
