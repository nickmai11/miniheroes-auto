#!/usr/bin/env python3
# Gear catch-up: Enhance every gear of the first N heroes (expanded hero list order) up to a target level. Gold only, never gems.
# usage: D=<serial> scripts/gear.py [--heroes 15] [--target 150 | --reset-below 135]     (hero screen must be open; ends on it)
#        --reset-below L: instead of enhancing, Reset (100% materials back) every gear with 0 < LV < L (Dino 2026-11-09);
#        --all: then the heroes past the 15th too (hero list kept open and scrolled; reset mode only); --swipe px (480 = 3 rows)
# Mapped on PuPu 2026-11-06 (1080x1920): grid 5 x 3 rows visible above the class filter bar, slots at x=120, y=400/550/700/850,
# popup "LV.N >> N+1" + gold "have/need" + Enhance. Stops (exit 1) on a missing Enhance button (purchase dialog) or have < need.
import re, sys, time
from flow import Stop, find, main, ocr, swipe, tap_wait, wait

COLS, ROWS = (140, 336, 536, 734, 932), (1250, 1490, 1690)   # row 3 is half under the filter bar: tap its visible top
SLOTS = (400, 550, 700, 850)
LV = r'L[Vv]\.?\s*(\d+)'


def num(t): return int(float(t.rstrip('kKmM')) * {'k': 1e3, 'm': 1e6}.get(t[-1].lower(), 1))


def name(boxes): return next((t for x, y, w, h, t in boxes if y < 160 and x < 500), '')


def popup_level(boxes):
    for x, y, w, h, t in boxes:
        m = re.fullmatch(LV, t.strip().replace('O', '0'))    # "LV.O" = LV.0 after a reset (Dino 2026-11-09)
        if m and 340 < y < 460: return int(m.group(1))
    return None


def gold(boxes):
    for x, y, w, h, t in boxes:
        m = re.search(r'([\d.]+[kKmM]?)\s*/\s*([\d.]+[kKmM]?)$', t.strip())
        if m and 1180 < y < 1300: return num(m.group(1)), num(m.group(2))
    return None


def slot_levels(boxes):
    """{slot index: level} from the 4 labels left of the hero (x<130); a missing label = locked/empty slot."""
    out = {}
    for x, y, w, h, t in boxes:
        if x + w // 2 < 130 and re.fullmatch(r'\d{1,3}', t.strip()):
            for i, sy in enumerate(SLOTS):
                if abs(y + h // 2 - (sy - 40)) < 45: out[i] = int(t)
    return out


def enhance(slot, target):
    tap_wait(120, SLOTS[slot])
    boxes = wait(r'^Enhance$', 5, (200, 1300, 880, 1460))
    lv = popup_level(boxes)
    if lv is None: raise Stop(f'slot {slot + 1}: popup level unreadable')
    n = 0
    while lv < target:
        g = gold(boxes)
        if g and g[0] < g[1]: print(f'  slot {slot + 1}: LV.{lv}, gold {g[0]} < {g[1]} -> out of gold', flush=True); break
        e = find(boxes, r'^Enhance$', (200, 1300, 880, 1460))
        if not e: raise Stop(f'slot {slot + 1}: Enhance button gone at LV.{lv} (purchase dialog?)')
        tap_wait(*e); n += 1
        for _ in range(5):
            boxes = ocr(); lv2 = popup_level(boxes)
            if lv2 is not None and lv2 > lv: break
            time.sleep(0.5)
        else:
            if lv2 == lv: print(f'  slot {slot + 1}: LV.{lv} unchanged after Enhance; stopped', flush=True); break
            raise Stop(f'slot {slot + 1}: level unreadable after Enhance from LV.{lv}')
        lv = lv2
    print(f'  slot {slot + 1}: Enhance x{n} -> LV.{lv}', flush=True)
    tap_wait(540, 120); wait(r'^Level Up$', 5, (200, 1050, 880, 1300))
    return lv


def reset(slot, below, after=r'^Level Up$'):
    """Gear popup -> Reset (bottom right) -> "Reset and return" preview (100% of the materials back, free) -> Confirm ->
    Congratulations -> LV.0. Mapped on Dino 2026-11-09 (Nick: reset every gear under LV.135). The popup's LV.N decides,
    not the side label (Shadow Fiend's 200 read as 22 there). `after` = what to wait for once the popup is closed
    (None while the hero list is open and covers Level Up)."""
    tap_wait(120, SLOTS[slot])
    boxes = wait(r'^Enhance$|^Reset$', 5, (200, 1300, 1000, 1460))
    lv = popup_level(boxes)
    if lv is None: raise Stop(f'slot {slot + 1}: popup level unreadable')
    if not 0 < lv < below:
        print(f'  slot {slot + 1}: popup says LV.{lv} -> left alone', flush=True); tap_wait(540, 120); time.sleep(0.5); return lv
    r = find(boxes, r'^Reset$', (780, 1300, 1000, 1460))
    if not r: raise Stop(f'slot {slot + 1}: no Reset button')
    tap_wait(*r); boxes = wait(r'Reset and return', 5)
    c = find(boxes, r'^Confirm$')
    if not c: raise Stop(f'slot {slot + 1}: Reset preview without Confirm')
    refund = ' '.join(t.strip() for x, y, w, h, t in boxes if 900 < y + h // 2 < 1060 and re.fullmatch(r'[\d.]+[kKmM]?', t.strip()))
    tap_wait(*c); wait(r'Tap anywhere|Congratulations', 8)
    tap_wait(540, 120); time.sleep(0.6)
    lv2 = popup_level(ocr())
    print(f'  slot {slot + 1}: LV.{lv} reset -> LV.{lv2} (returned {refund})', flush=True)
    if lv2 != 0: raise Stop(f'slot {slot + 1}: reads LV.{lv2} after the Reset')
    tap_wait(540, 120)
    if after: wait(after, 5, (200, 1050, 880, 1300))
    else: time.sleep(0.6)
    return lv2


def run_scrolled(below, seen, dy=480):
    """Heroes past the 15th (Dino 2026-11-09): the hero list stays open across card taps and gear popups, so it is expanded
    once and scrolled with slow swipes (a fast one glides); re-expanding resets it to the top. Cards are found by their
    'Lv.N' labels (OCR), each tapped once, the hero name checked against `seen`. Stops after 2 swipes with nothing new."""
    tap_wait(1008, 1400); time.sleep(0.5)
    idle = 0
    while idle < 2:
        swipe(540, 1170 + dy, 540, 1170, 1500); time.sleep(1.2)   # 480 px slow = 3 rows on Dino; smaller = overlapping passes
        labels = sorted(((y + h // 2, x + w // 2) for x, y, w, h, t in ocr()
                         if re.search(r'\d{2,3}$', t.strip()) and len(t.strip()) <= 7 and 1120 < y + h // 2 < 1700 and x + w // 2 < 1000),
                        key=lambda p: (p[0] // 120, p[1]))
        new = 0
        for ly, lx in labels:
            tap_wait(lx + 40, ly + 60); time.sleep(0.5); b = ocr(); hero = name(b)
            if not hero or hero in seen: continue
            seen.append(hero); new += 1; levels = slot_levels(b)
            print(f'{len(seen)}. {hero}: gear {[levels.get(s) for s in range(4)]}', flush=True)
            for s in range(4):
                if s in levels and 0 < levels[s] < below: reset(s, below, after=None)
        idle = idle + 1 if new == 0 else 0
    tap_wait(1008, 1100); wait(r'^Level Up$', 5, (200, 1050, 880, 1300))


def run(n_heroes=15, target=150, reset_below=None, scrolled=False, dy=480):
    seen = []
    for i in range(n_heroes):
        tap_wait(1008, 1400)                                  # expand the hero list
        time.sleep(0.5)
        tap_wait(COLS[i % 5], ROWS[i // 5])
        tap_wait(1008, 1100)                                  # close the list
        boxes = wait(r'^Level Up$', 6, (200, 1050, 880, 1300))
        hero = name(boxes)
        if not hero or hero in seen: raise Stop(f'hero {i + 1}: name {hero!r} (already done: {seen})')
        seen.append(hero)
        levels = slot_levels(boxes)
        print(f'{i + 1}. {hero}: gear {[levels.get(s) for s in range(4)]}', flush=True)
        for s in range(4):
            if s not in levels: print(f'  slot {s + 1}: no level label (locked/empty) -> skipped', flush=True); continue
            if reset_below is not None:
                if 0 < levels[s] < reset_below: reset(s, reset_below)
            elif levels[s] < target: enhance(s, target)
    if scrolled and reset_below is not None: run_scrolled(reset_below, seen, dy)
    print('gear done')


if __name__ == '__main__':
    a = sys.argv[1:]
    g = lambda k, d: int(a[a.index(k) + 1]) if k in a else d
    main(lambda _: run(g('--heroes', 15), g('--target', 150), g('--reset-below', None), '--all' in a, g('--swipe', 480)), 'gear')
