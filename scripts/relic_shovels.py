#!/usr/bin/env python3
# Relic shovels: buy shovel packs with gems while the price is <= relic_shovels.max_gem_price (Nick, 2026-10-28: 80).
# usage: D=<serial> scripts/relic_shovels.py <account>     (main screen; ends on the main screen)
# Path (mapped on Cmajor 2026-10-28): Relic (972,1788) -> Lost Continent map -> Archaeology (536,1632) -> dig board ->
# green "+" on the shovel button (650,1770) -> Tip "Spend P diamonds to buy N Shovel? (Remaining purchases: R)"
# -> Confirm (538,1158) / close ✕ (938,636). The price is read before every Confirm; shovels N/150 must go up.
# Never digs, never One-Tap Mining / drill / bomb. exit 1 = unexpected screen (v_relic_shovels.png).
import os, re, sys, time
from flow import Stop, joined, main, ocr, tap_wait, wait

HERE = os.path.dirname(os.path.abspath(__file__))


def shovels(boxes):
    return next((int(t.split('/')[0]) for x, y, w, h, t in boxes if x < 300 and 330 < y < 480 and re.fullmatch(r'\d+/\d+', t.strip())), None)  # N/150 (Cmajor), N/100 (Kong)


def run(account):
    cfg = open(os.path.join(HERE, '..', 'accounts', account + '.yaml')).read()
    m = re.search(r'relic_shovels:.*\n\s+max_gem_price:\s*(\d+)', cfg)
    if not m: print('relic_shovels not in config; skip'); return 0
    cap = int(m.group(1))
    tap_wait(972, 1788); wait(r'Archaeology', 10)
    tap_wait(536, 1632); boxes = wait(r'One-Tap|Mine \d+ more', 10)
    bought = []
    for _ in range(5):
        n = shovels(boxes)
        tap_wait(650, 1770)
        t = joined(wait(r'Spend \d+ diamonds', 6))
        p = re.search(r'Spend (\d+) diamonds to buy (\d+)', t)
        if not p: raise Stop(f'shovel price unreadable: {t[:150]}')
        price, qty = int(p.group(1)), int(p.group(2))
        if price > cap:
            tap_wait(938, 636); print(f'next shovel pack costs {price} > {cap}; not bought'); break
        tap_wait(538, 1158); time.sleep(1.5)
        boxes = ocr()
        if 'Spend' in joined(boxes): tap_wait(938, 636); boxes = ocr()   # popup reopened with the next price
        n2 = shovels(boxes)
        if n is None or n2 is None or n2 < n + qty: raise Stop(f'shovels {n} -> {n2} after buying {qty} for {price}')
        bought.append(price); print(f'bought {qty} shovels for {price} gems ({n} -> {n2})', flush=True)
    tap_wait(92, 1830); wait(r'Archaeology', 8)       # board -> map
    tap_wait(80, 1820)                                # map -> main screen
    print(f'relic shovels done: paid {bought or "nothing"}')


if __name__ == '__main__':
    main(run, sys.argv[1])
