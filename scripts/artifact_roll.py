#!/usr/bin/env python3
# Artifact Auto Wish loop (Recruit -> Artifact tab): Wish with Auto ticked, every CYCLE (20) s tap outside the
# "Auto Wish" box (cancel -> "Congratulations ... Tap anywhere to close" summary), close it, Wish again.
# A new artifact pops a big "Congratulations / <name> / Confirm" display over the box. Red name = Mythic -> stop
# (Nick 2026-11-02: stop on a new Mythic only); other colours (orange = Legendary, Slumber Staff) -> Confirm, go on.
# Box gone with no Confirm / "Mythic" text -> stop. Brilliance tier reached -> cancel and restart at once (Nick 2026-11-02). Costs stars (200-250 per wish). Guards: refuses a Wish showing the 280 gem price, and
# stops if the gem count ever drops. usage: D=<serial> scripts/artifact_roll.py [max_cycles]   (from the Artifact tab)
# exit 1 / found -> v_artifact_roll.png. Mapped on Cmajor 2026-11-02.
import re, sys, time
from flow import Stop, find, grab, joined, main, ocr, tap, tap_wait, wait

CYCLE = 20                          # Nick 2026-11-02 (was 30)
GEMS = (60, 40, 260, 100)          # top-left gem counter
CLOSE = (540, 250)                 # empty spot above the box / anywhere on the summary
OUTSIDE = (540, 1092)              # "Stops when 100 Wishes..." line, just below the Auto Wish box
NAME = (300, 1184, 780, 1228)      # artifact name band on the new-artifact display
CONFIRM = (540, 1616)
BRILLIANCE = (742, 1243)           # top edge of the Brilliance tier frame: tan (R~206) when it's the current tier, else R~25


def gems(boxes):
    x0, y0, x1, y1 = GEMS
    g = [t for x, y, w, h, t in boxes if x0 <= x + w // 2 <= x1 and y0 <= y + h // 2 <= y1 and re.fullmatch(r'\d+', t)]
    if not g: raise Stop(f'gem counter unreadable: {joined(boxes)[:200]}')
    return int(g[0])


def red_name(im):
    """Mythic = red name (Nick). Legendary orange is (255,180,59): G well above 100."""
    x0, y0, x1, y1 = NAME
    return sum(r > 190 and g < 100 and b < 100 for r, g, b in (im.getpixel((x, y)) for x in range(x0, x1, 2) for y in range(y0, y1, 2))) > 50


def mythic(boxes): return find(boxes, r'(?i)mythic')


def run(max_cycles=1000):
    boxes = wait(r'^Wish$', 10, (300, 1580, 780, 1700))
    g0 = gems(boxes)
    for n in range(1, int(max_cycles) + 1):
        if find(boxes, r'^280$', (300, 1580, 780, 1700)): raise Stop('Wish shows 280 (gem price), not paying')
        if not find(boxes, r'^Auto$', (840, 1620, 1040, 1700)): raise Stop('Auto toggle not found')
        tap_wait(540, 1638)                                        # Wish (Auto ticked -> Auto Wish box)
        wait(r'Auto Wish', 6)
        t0, cancel = time.time(), True
        while time.time() - t0 < CYCLE:
            im = grab(); boxes = ocr(im)
            if im.getpixel(BRILLIANCE)[0] > 120 and find(boxes, r'Auto Wish'):
                print(f'cycle {n}: Brilliance reached -> restart'); break    # Nick 2026-11-02: restart at once
            if mythic(boxes) or not find(boxes, r'Auto Wish'):
                if mythic(boxes) or red_name(im) or not find(boxes, r'^Confirm$'):
                    print(f'cycle {n}: new Mythic (red name) / box gone: {joined(boxes)[:300]}')
                    raise Stop('found')
                name = ' '.join(t for x, y, w, h, t in boxes if NAME[1] <= y + h // 2 <= NAME[3])
                print(f'cycle {n}: new non-Mythic {name!r} -> Confirm, go on')
                tap_wait(*CONFIRM); boxes = ocr()
                if not find(boxes, r'Auto Wish'): cancel = False; break   # auto ended -> summary / Wish below
                continue
            if gems(boxes) < g0: tap(*OUTSIDE); raise Stop(f'gems dropped {g0} -> {gems(boxes)}')
            time.sleep(1.5)
        if cancel: tap_wait(*OUTSIDE)                              # cancel
        boxes = wait(r'(?i)tap anywhere to close|mythic|^Wish$', 8)
        if mythic(boxes): raise Stop('found')
        if find(boxes, r'(?i)tap anywhere'): tap_wait(*CLOSE)
        boxes = wait(r'^Wish$', 8, (300, 1580, 780, 1700))
        if gems(boxes) < g0: raise Stop(f'gems dropped {g0} -> {gems(boxes)}')
        print(f'cycle {n} done')


if __name__ == '__main__':
    main(run, *sys.argv[1:])
