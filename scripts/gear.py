#!/usr/bin/env python3
# Gear catch-up: Enhance every gear of the first N heroes (expanded hero list order) up to a target level. Gold only, never gems.
# usage: D=<serial> scripts/gear.py [--heroes 15] [--target 150]     (hero screen must be open; ends on it)
# Mapped on PuPu 2026-11-06 (1080x1920): grid 5 x 3 rows visible above the class filter bar, slots at x=120, y=400/550/700/850,
# popup "LV.N >> N+1" + gold "have/need" + Enhance. Stops (exit 1) on a missing Enhance button (purchase dialog) or have < need.
import re, sys, time
from flow import Stop, find, main, ocr, tap_wait, wait

COLS, ROWS = (140, 336, 536, 734, 932), (1250, 1490, 1690)   # row 3 is half under the filter bar: tap its visible top
SLOTS = (400, 550, 700, 850)
LV = r'L[Vv]\.?\s*(\d+)'


def num(t): return int(float(t.rstrip('kKmM')) * {'k': 1e3, 'm': 1e6}.get(t[-1].lower(), 1))


def name(boxes): return next((t for x, y, w, h, t in boxes if y < 160 and x < 500), '')


def popup_level(boxes):
    for x, y, w, h, t in boxes:
        m = re.fullmatch(LV, t.strip())
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


def run(n_heroes=15, target=150):
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
            if levels[s] < target: enhance(s, target)
    print('gear done')


if __name__ == '__main__':
    a = sys.argv[1:]
    g = lambda k, d: int(a[a.index(k) + 1]) if k in a else d
    main(lambda _: run(g('--heroes', 15), g('--target', 150)), 'gear')
