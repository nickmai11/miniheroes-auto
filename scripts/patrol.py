#!/usr/bin/env python3
# Patrol: Speed Patrol while the price is Free or <= patrol.max_gem_price (never the 100 one), then Claim All.
# usage: D=<serial> scripts/patrol.py <account> [--claim-only]     (main screen must be open)
# The Tip shows "(Remaining chances today: N)" and a price button (Free / 50 / 100 …), both read with OCR before
# every tap; N must drop by 1 after each buy. exit 0 = done, 1 = unexpected screen (v_patrol.png).
# UNTESTED (written 2026-10-28 from saved screenshots) — run on one account first, watch it.
import os, re, sys, time
from flow import Stop, find, joined, main, ocr, tap, tap_wait, wait

HERE = os.path.dirname(os.path.abspath(__file__))


def tip():
    """(chances or None, price) from the open Tip; price 0 = Free. The Free Tip has no chances line."""
    boxes = wait(r'Patrol G|Obta|Remaining chances', 8)
    m = re.search(r'Remaining chances today\W*(\d+)', joined(boxes))
    btn = [t for x, y, w, h, t in boxes if 1080 < y + h // 2 < 1250 and 300 < x + w // 2 < 780]
    price = 0 if any(re.search(r'Free|Miễn', t) for t in btn) else next((int(t) for t in btn if t.strip().isdigit()), None)
    if price is None: raise Stop(f'Tip price unreadable: {joined(boxes)[:200]}')
    return (int(m.group(1)) if m else None), price


def run(account, claim_only=False):
    cfg = open(os.path.join(HERE, '..', 'accounts', account + '.yaml')).read()
    cap = int(re.search(r'patrol:(?:\n\s+.*)*?\n\s+max_gem_price:\s*(\d+)', cfg).group(1))
    tap_wait(983, 1463)                                   # patrol bag -> Loot dialog
    wait(r'Speed Patrol', 8)
    bought = []
    if not claim_only:
        tap_wait(337, 1590)
        while len(bought) < 10:
            n, price = tip()
            if price >= 100 or price > cap:
                print(f'next Speed Patrol costs {price} gems; not bought'); break
            if n == 0: print('no Speed Patrol chances left'); break
            tap_wait(540, 1164)                           # buy -> Congratulations
            wait(r'Congratulations|Tap anywhere', 6); tap_wait(540, 1700)
            n2, _ = tip()                                 # the Tip reopens with the next price
            if n is not None and n2 != n - 1: raise Stop(f'chances {n} -> {n2} after a Speed Patrol')
            bought.append(price or 'Free'); print(f'Speed Patrol: {price or "Free"}', flush=True)
        tap_wait(936, 638)                                # close the Tip
        wait(r'Claim All', 8)
    p = find(ocr(), r'Claim All')
    if not p: raise Stop('Claim All not found')
    tap_wait(*p); time.sleep(2); tap_wait(540, 1880)      # Congratulations (auto-closes) -> dismiss at the very bottom
    print(f'patrol done: speed {bought}, Claim All tapped')


if __name__ == '__main__':
    main(run, sys.argv[1], '--claim-only' in sys.argv)
