#!/usr/bin/env python3
# Hero upgrade: config hero +hero_levels (Level Up), 1st gear +gear_levels (Enhance). Potions/gold only, never gems.
# usage: D=<serial> scripts/hero.py <account>     (main screen must be open; ends on the hero screen)
# Finds the hero by its avatar (template <hero>_strip.png, face only) in the expanded list, Marksman filter, from the bottom.
# Level "Lv.N" is read before and after every Level Up (+1); the gear popup opens once, Enhance x gear_levels, no read-back
# (levels don't matter: Bone Archer is only for the dailies, Nick 2026-11-03).
# Never taps Quick Ascend or Reset. Rebirth + the "↑ Lv.90" quick button ONLY when out of potions (rebirth_90, Nick 2026-11-03).
import os, re, sys, time
from flow import Stop, find, find_img, grab, main, ocr, swipe, tap, tap_text, tap_wait, wait

HERE = os.path.dirname(os.path.abspath(__file__))


def name(boxes): return next((t for x, y, w, h, t in boxes if y < 160 and x < 500), '')


def level(boxes, region, pat=r'L[Vv]\.?\s*(\d+)'):
    x0, y0, x1, y1 = region
    for x, y, w, h, t in boxes:
        m = re.fullmatch(pat, t.strip())
        if m and x0 <= x + w // 2 <= x1 and y0 <= y + h // 2 <= y1: return int(m.group(1))
    return None


def settle(region=(0, 1420, 1080, 1700)):
    """Wait until the list stops coasting: taps on a moving list pick the wrong card (Aminor 2026-10-29). <2% of the
    samples changed = still - card shine / red dots keep animating, an exact match never came (79 s select, 2026-11-03)."""
    a = list(grab().crop(region).getdata())[::97]
    for _ in range(10):
        time.sleep(0.3); b = grab(); c = list(b.crop(region).getdata())[::97]
        if sum(p != q for p, q in zip(a, c)) < len(c) // 50: return b
        a = c
    return b


def same(a, b): return sum(p != q for p, q in zip(a, b)) < len(b) // 50


GRID = (0, 1130, 1080, 1720)                                    # expanded hero list, above the class filter bar


def select(hero):
    """Expanded hero list (icon above the strip) -> Marksman filter -> bottom -> the hero's card by its avatar
    (Nick 2026-11-03): template `<hero>_strip.png` = face only, between the Lv label and the stars. It isn't always the
    last card (Bino: one Lv.160 after it) -> search up from the bottom. Name top-left confirms; grid closed with its X.
    Scores: Bone Archer 9-15, other cards ~50 (8 accounts' strips + Bino's grid)."""
    if hero.lower() in name(ocr()).lower(): return
    tpl = os.path.join(HERE, hero.lower().replace(' ', '_') + '_strip.png')
    if not os.path.exists(tpl): raise Stop(f'no avatar template {os.path.basename(tpl)} for {hero!r}')
    tap_wait(1008, 1400)                                        # expand the hero list
    tap_wait(662, 1800)                                         # Marksman (the game keeps it; a 2nd tap keeps it on)
    prev = None
    for _ in range(8):                                          # to the bottom: swipe until the grid stops moving
        swipe(540, 1600, 540, 1150, 300)
        cur = list(settle(GRID).crop(GRID).getdata())[::97]
        if prev and same(cur, prev): break
        prev = cur
    for _ in range(8):                                          # then up a page at a time
        im = settle(GRID); x, y, d = find_img(tpl, GRID, im)
        if d < 30: break
        cur = list(im.crop(GRID).getdata())[::97]
        swipe(540, 1250, 540, 1650, 300)
        if same(list(settle(GRID).crop(GRID).getdata())[::97], cur): raise Stop(f'{hero!r} avatar not in the hero list')
    else: raise Stop(f'{hero!r} avatar not in the hero list')
    tap_wait(x, y)
    if hero.lower() not in name(ocr()).lower(): raise Stop(f'tapped {hero} avatar (diff {d}) but the name reads {name(ocr())!r}')
    tap_wait(1008, 1100); wait(r'^Level Up$', 5, (200, 1050, 880, 1300))   # close the list


def num(t):
    """'239k' -> 239000, '1.2M' -> 1200000, '500' -> 500."""
    return int(float(t.rstrip('kKmM')) * {'k': 1e3, 'm': 1e6}.get(t[-1].lower(), 1))


def potions(boxes):
    """(have, need) from the potion line above Level Up ("18M/30300"), or None."""
    for x, y, w, h, t in boxes:
        m = re.search(r'([\d.]+[kKmM]?)\s*/\s*([\d.]+[kKmM]?)$', t.strip())   # icon reads as ')' (Kong)
        if m and 980 < y < 1140: return num(m.group(1)), num(m.group(2))


def confirm(title, timeout=6):
    """Tap the dialog's Confirm until its title is gone - a tap during the pop-in animation is ignored (Cmajor 2026-11-03)."""
    for _ in range(3):
        tap_text(r'^Confirm$', boxes=wait(r'^Confirm$', 5))
        t0 = time.time()
        while time.time() - t0 < timeout:
            if not find(ocr(), title): return
            time.sleep(0.5)
    raise Stop(f'{title}: Confirm ignored 3x')


def rebirth_90(hero):
    """Not enough potions for the next level (Nick 2026-11-03): Rebirth (free, 100% of the hero AND gear materials back -
    the gear resets to 0 too), Level Up once, then the "↑ Lv.90" quick button -> Quick Level Up (potions) -> Lv.90.
    Mapped on Cmajor 2026-11-03 (Lv.96 -> 1 -> 2 -> 90)."""
    r = find(ocr(), r'^Rebirth$')
    if not r: raise Stop('no Rebirth button')
    tap_wait(r[0], r[1] - 40)                               # icon above the label
    b = wait(r'Rebirth Preview', 5)
    if not find(b, r'100%'): raise Stop('Rebirth Preview without the 100% refund line')
    confirm('Rebirth Preview'); wait(r'Congratulations', 6); tap_wait(540, 120)
    b = wait(r'^Level Up$', 6, (200, 1050, 880, 1300))
    if level(b, (300, 340, 800, 460)) != 1: raise Stop('hero not at Lv.1 after Rebirth')
    tap_wait(*find(b, r'^Level Up$', (200, 1050, 880, 1300)))
    b = wait(r'Lv\.90$', 6, (200, 980, 880, 1110))         # quick button "↑ Lv.90" appears above Level Up
    tap_wait(*find(b, r'Lv\.90$', (200, 980, 880, 1110)))
    b = wait(r'Quick Level Up', 5)
    if not find(b, r'Lv\.90') or not any(re.search(r'[\d.]+[kKmM]?/[\d.]+[kKmM]?$', t.strip()) for *_, t in b):
        raise Stop('Quick Level Up: not "-> Lv.90" for potions; stop')    # never a gem price
    confirm('Quick Level Up')
    for _ in range(6):
        lv = level(ocr(), (300, 340, 800, 460))
        if lv == 90: break
        time.sleep(0.7)
    else: raise Stop(f'Lv.{lv} after Quick Level Up, expected 90')
    print(f'{hero}: out of potions -> Rebirth -> Lv.1 -> Level Up -> quick Lv.90 (gear reset to 0)', flush=True)


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
        for _ in range(7):        # poll: a single read mid-animation failed Aminor after 4 levels (2026-11-03)
            boxes = ocr(); lv = level(boxes, (300, 340, 800, 460))
            p = find(boxes, r'^Level Up$', (200, 1050, 880, 1300))
            if lv is not None and p: break
            time.sleep(0.7)
        else: raise Stop('hero level / Level Up not readable')
        tap_wait(*p); time.sleep(1)
        for _ in range(4):                                   # label redraws after the tap: re-read before deciding
            lv2 = level(ocr(), (300, 340, 800, 460))
            if lv2 is not None and lv2 != lv: break
            time.sleep(1)
        if lv2 is None:   # unreadable != failed: a FAIL got retried and levelled again (Cmajor 63->64->65, 2026-11-01)
            print(f'{hero} level unreadable after Level Up from {lv}; counted as levelled, not retried', flush=True); continue
        if lv2 == lv:
            pot = potions(ocr())
            # real shortage only: Kong's Lv.170 didn't move with 1557k/1351k potions (cap/Upgrade?, 2026-11-03)
            if pot and pot[0] < pot[1] and lv > 90: rebirth_90(hero); break
            print(f'{hero}: Lv.{lv} unchanged after Level Up (potions {pot}); stopped levelling', flush=True); break
        if lv2 != lv + 1: raise Stop(f'{hero} level {lv} -> {lv2} after one Level Up')
        print(f'{hero}: Lv.{lv} -> Lv.{lv2}', flush=True)
    if n_gear > 0:                                           # open the gear popup ONCE, Enhance n times (Nick 2026-11-03)
        for y in (360, 400):                                 # slot 1 sits at 360 or 400 depending on the account
            tap_wait(117, y)
            try: boxes = wait(r'^Enhance$', 4, (200, 1300, 880, 1460)); break   # poll, popup animates in (Kong 2026-11-03)
            except Stop: tap_wait(540, 120)
        else: raise Stop('gear popup (Enhance) did not open')
        e, n = find(boxes, r'^Enhance$', (200, 1300, 880, 1460)), 0
        for _ in range(n_gear):                              # levels don't matter (Nick) - no read-back; but the
            tap_wait(*e); n += 1; time.sleep(0.3)            # button must still be there: out of gold may pop a
            if not find(ocr(), r'^Enhance$', (200, 1300, 880, 1460)): break   # purchase dialog -> never tap into it
        print(f'gear 1: Enhance x{n}', flush=True)
        tap_wait(540, 120)
    print('hero upgrade done')


if __name__ == '__main__':
    main(run, sys.argv[1])
