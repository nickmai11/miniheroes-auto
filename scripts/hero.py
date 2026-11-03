#!/usr/bin/env python3
# Hero upgrade: config hero +hero_levels (Level Up), 1st gear +gear_levels (Enhance). Potions/gold only, never gems.
# usage: D=<serial> scripts/hero.py <account>     (main screen must be open; ends on the hero screen)
# Finds the hero by name: taps strip cards from the end (lowest CP) back, cards found from the grey gaps.
# Level "Lv.N" / gear "LV.N" are read before and after every tap and must go up by exactly 1.
# Never taps the "↑ Lv.N" quick-level buttons, Quick Ascend, Rebirth or Reset (only exact "Level Up" / "Enhance").
# UNTESTED (written 2026-10-28 from saved screenshots) — run on one account first, watch it.
import datetime, os, re, sys, time
from flow import Stop, find, grab, main, ocr, swipe, tap, tap_wait, wait

HERE = os.path.dirname(os.path.abspath(__file__))


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


def cards(im, y=1620):
    """Card centre x's, read from the strip itself: cards are the runs between the grey (189,190,197) gaps — no
    "Lv.N" labels, no card pitch (Nick 2026-11-03: OCR missed "Lv.97" and the hero on xFaktor)."""
    runs, x0 = [], None
    for x in range(1081):
        grey = x == 1080 or sum(abs(a - b) for a, b in zip(im.getpixel((x, y))[:3], (189, 190, 197))) < 15
        if not grey and x0 is None: x0 = x
        if grey and x0 is not None:
            if runs and x0 - runs[-1][1] < 6: runs[-1][1] = x      # a stray grey pixel inside a card
            else: runs.append([x0, x])
            x0 = None
    return [(a + b) // 2 for a, b in runs if b - a > 100]


def select(hero):
    """The config hero is among the lowest-CP heroes = at the END of the strip (Nick, 2026-10-29): try every card
    right to left, page by page back to the start. Re-swipe before every tap (a tap can shift the strip, Aminor)."""
    if hero.lower() in name(ocr()).lower(): return
    page, i, prev = 0, 0, None
    while True:
        for _ in range(15): swipe(950, 1536, 150, 1536, 300)
        for _ in range(page): swipe(150, 1536, 950, 1536, 300)
        settle(); im = grab(); xs = cards(im)[::-1]
        if i >= len(xs):
            strip = list(im.crop((0, 1420, 1080, 1700)).getdata())[::97]
            if strip == prev: raise Stop(f'{hero!r} not on the hero strip')   # back-swipe didn't move: start reached
            prev, page, i = strip, page + 1, 0; continue
        tap_wait(xs[i], 1580); i += 1
        if hero.lower() in name(ocr()).lower(): return


def run(account):
    cfg = open(os.path.join(HERE, '..', 'accounts', account + '.yaml')).read()
    block = re.search(r'hero_upgrade:\s*\n((?:\s+\w+:.*\n)+)', cfg).group(1)
    get = lambda k, d=0: (re.search(rf'{k}:\s*(.+)', block) or [None, d])[1]
    hero, n_lv, slot, n_gear = get('hero').strip(), int(get('hero_levels')), int(get('gear_slot', 1)), int(get('gear_levels'))
    if slot != 1: raise Stop(f'gear_slot {slot} not mapped (only slot 1)')
    # daily cap, not per run: a retry restarted at 0 and took Aminor +9 instead of +5 (2026-11-03)
    day = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=5)).date()
    try: done = open(os.path.join(HERE, '..', 'logs', account, f'{day}.log')).read()
    except OSError: done = ''
    n_lv -= len(re.findall(rf'{re.escape(hero)}: Lv\.\d+ -> Lv\.\d+', done))
    n_gear -= len(re.findall(r'gear 1: LV\.\d+ -> LV\.\d+', done))
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
        if lv2 == lv:     # out of potions: normal with 5 level-ups/day (Nick 2026-11-02) -> on to the gear
            print(f'{hero}: Lv.{lv} unchanged after Level Up (not enough potions?); stopped levelling', flush=True); break
        if lv2 != lv + 1: raise Stop(f'{hero} level {lv} -> {lv2} after one Level Up')
        print(f'{hero}: Lv.{lv} -> Lv.{lv2}', flush=True)
    for _ in range(n_gear):
        for y in (360, 400):                                 # slot 1 sits at 360 or 400 depending on the account
            tap_wait(117, y)
            try: boxes = wait(r'^Enhance$', 4, (200, 1300, 880, 1460)); break   # poll, popup animates in (Kong 2026-11-03)
            except Stop: tap_wait(540, 120)
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
