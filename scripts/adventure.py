#!/usr/bin/env python3
# Adventure battles with the pre-selected lineup: Tower of the Throne (config count) and Beast Realm (1 challenge).
# usage: D=<serial> scripts/adventure.py <account> tower|beast     (main screen must be open; ends on the mode screen)
# Tower: ticket count top-left must drop by 1 per fight; stops early at 0. Never "Challenge again", never pays
# for chances, never opens Shop. exit 1 = unexpected screen (v_adventure.png).
# UNTESTED (written 2026-10-28 from saved screenshots) — run on one account first, watch it.
import os, re, sys
from flow import Stop, adventure, battle, find, main, ocr, wait

HERE = os.path.dirname(os.path.abspath(__file__))


def tickets():
    return next((int(t) for x, y, w, h, t in ocr() if y < 120 and x < 300 and t.strip().isdigit()), None)


def run(account, mode):
    cfg = open(os.path.join(HERE, '..', 'accounts', account + '.yaml')).read()
    if mode == 'tower':
        n = int(re.search(r'tower_of_the_throne:\s*(\d+)', cfg).group(1))
        adventure(r'Tower of the Throne'); boxes = wait(r'^Challenge$|^Claim Reward$', 10, (0, 1600, 1080, 1920))
        if not find(boxes, r'^Challenge$', (0, 1600, 1080, 1920)):   # top floor cleared (Chien Than, Floor 2000, 2026-10-29)
            print('SKIP tower fully cleared (no Challenge; "Claim Reward" not mapped, left for Nick)'); return
        for i in range(n):
            t = tickets()
            if t == 0: print('tower: 0 tickets left'); break
            res = battle(r'Tower of the Throne', timeout=150)
            t2 = tickets()
            won = 'Victory' in res                         # a win costs no ticket (Chien Than 9 -> 9 at Floor 2020, 2026-11-01)
            if t is not None and t2 != t - 1 and not (won and t2 == t): raise Stop(f'tower tickets {t} -> {t2} after a fight')
            print(f'tower {i + 1}/{n}: {"Victory" if won else "Defeat" if "Defeat" in res else "?"}, tickets {t2}', flush=True)
            if find(ocr(), r'^Claim Reward$', (0, 1600, 1080, 1920)): print('tower: top floor cleared (Claim Reward)'); break
    elif mode == 'beast':
        adventure(r'Beast Realm'); wait(r'Next Beast', 10)
        res = battle(r'Next Beast', timeout=150)
        print(f'beast realm: 1 challenge done ({res[:60]})')
    else: raise Stop(f'unknown mode {mode}')


if __name__ == '__main__':
    main(run, sys.argv[1], sys.argv[2])
