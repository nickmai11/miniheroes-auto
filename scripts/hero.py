#!/usr/bin/env python3
# Hero upgrade: config hero +hero_levels (Level Up), 1st gear +gear_levels (Enhance). Potions/gold only, never gems.
# usage: D=<serial> scripts/hero.py <account>     (main screen must be open; ends on the hero screen)
# Finds the hero by tapping strip cards (their "Lv.N" labels give the x) and reading the name top-left.
# Level "Lv.N" / gear "LV.N" are read before and after every tap and must go up by exactly 1.
# Never taps the "↑ Lv.N" quick-level buttons, Quick Ascend, Rebirth or Reset (only exact "Level Up" / "Enhance").
# UNTESTED (written 2026-10-28 from saved screenshots) — run on one account first, watch it.
import os, re, sys, time
from flow import Stop, find, grab, main, ocr, swipe, tap, tap_wait, wait

HERE = os.path.dirname(os.path.abspath(__file__))
STRIP = (120, 1430, 1080, 1540)   # card "Lv.N" labels; the leftmost one is half under Quick Ascend (tap y 1580 is below it)


def name(boxes): return next((t for x, y, w, h, t in boxes if y < 160 and x < 500), '')


def level(boxes, region, pat=r'L[Vv]\.?\s*(\d+)'):
    x0, y0, x1, y1 = region
    for x, y, w, h, t in boxes:
        m = re.fullmatch(pat, t.strip())
        if m and x0 <= x + w // 2 <= x1 and y0 <= y + h // 2 <= y1: return int(m.group(1))
    return None


def settle():
    """Wait until the strip stops coasting: taps on a moving strip pick the wrong card (Aminor 2026-10-29)."""
    a = grab().crop((0, 1420, 1080, 1700))
    for _ in range(10):
        time.sleep(0.4); b = grab().crop((0, 1420, 1080, 1700))
        if list(a.getdata())[::97] == list(b.getdata())[::97]: return
        a = b


def fill(xs):
    """Insert cards between two read labels 2+ card pitches (~190 px) apart."""
    out = xs[:1]
    for a, b in zip(xs, xs[1:]):
        k = round((b - a) / 190)
        out += [a + (b - a) * i // k for i in range(1, k)] + [b]
    return out


def select(hero):
    boxes = ocr()
    if hero.lower() in name(boxes).lower(): return
    for _ in range(15): swipe(950, 1536, 150, 1536, 300)   # strip to the end (Bone Archer is usually near it)
    settle()
    seen = None
    for page in range(25):
        boxes = ocr()
        # partial labels count: Quick Ascend hides "Lv.1" ("60", Dminor), OCR drops the L ("V.91", Aminor) — 2026-10-29
        # ".91" too (Aminor); fill() adds cards whose label wasn't read at all ("Lv.157", Aminor)
        cards = fill(sorted({x + w // 2 for x, y, w, h, t in boxes if re.match(r'([LlI]?[Vv])?\.?\s*\d+$', t.strip())
                             and STRIP[0] <= x + w // 2 <= STRIP[2] and STRIP[1] <= y + h // 2 <= STRIP[3]}))[::-1]
        if cards == seen: break                               # strip did not move: start reached
        seen = cards
        for cx in cards:
            tap_wait(cx, 1580)
            if hero.lower() in name(ocr()).lower(): return
        swipe(150, 1536, 950, 1536, 300); settle()            # one page back towards the start
    raise Stop(f'{hero!r} not found in the hero strip')


def run(account):
    cfg = open(os.path.join(HERE, '..', 'accounts', account + '.yaml')).read()
    block = re.search(r'hero_upgrade:\s*\n((?:\s+\w+:.*\n)+)', cfg).group(1)
    get = lambda k, d=0: (re.search(rf'{k}:\s*(.+)', block) or [None, d])[1]
    hero, n_lv, slot, n_gear = get('hero').strip(), int(get('hero_levels')), int(get('gear_slot', 1)), int(get('gear_levels'))
    if slot != 1: raise Stop(f'gear_slot {slot} not mapped (only slot 1)')
    tap_wait(274, 1810)                                      # Hero
    wait(r'^Level Up$', 10)
    select(hero)
    for _ in range(n_lv):
        boxes = ocr(); lv = level(boxes, (300, 340, 800, 460))
        p = find(boxes, r'^Level Up$', (200, 1050, 880, 1300))
        if lv is None or not p: raise Stop('hero level / Level Up not readable')
        tap_wait(*p); time.sleep(1)
        lv2 = level(ocr(), (300, 340, 800, 460))
        if lv2 != lv + 1: raise Stop(f'{hero} level {lv} -> {lv2} after one Level Up (not enough potions?)')
        print(f'{hero}: Lv.{lv} -> Lv.{lv2}', flush=True)
    for _ in range(n_gear):
        for y in (360, 400):                                 # slot 1 sits at 360 or 400 depending on the account
            tap_wait(117, y)
            boxes = ocr()
            if find(boxes, r'^Enhance$', (200, 1300, 880, 1460)): break
            tap_wait(540, 120)
        else: raise Stop('gear popup (Enhance) did not open')
        lv = level(boxes, (600, 330, 1000, 450))
        tap_wait(*find(boxes, r'^Enhance$', (200, 1300, 880, 1460))); time.sleep(1)
        lv2 = level(ocr(), (600, 330, 1000, 450))
        if lv is None or lv2 != lv + 1: print(f'gear: LV {lv} -> {lv2} (could not verify +1 — check the badge)')
        else: print(f'gear 1: LV.{lv} -> LV.{lv2}', flush=True)
        tap_wait(540, 120)
    print('hero upgrade done')


if __name__ == '__main__':
    main(run, sys.argv[1])
