#!/usr/bin/env python3
# Adventure battles with the pre-selected lineup: Tower of the Throne (config count) and Beast Realm (1 challenge).
# usage: D=<serial> scripts/adventure.py <account> tower|beast     (main screen must be open; ends on the mode screen)
# Tower: Bone Archer alone (flow.lone_hero, Nick 2026-11-02); ticket count top-left must drop by 1 per fight; stops early at 0. Never "Challenge again", never pays
# for chances, never opens Shop. exit 1 = unexpected screen (v_adventure.png).
# UNTESTED (written 2026-10-28 from saved screenshots) — run on one account first, watch it.
import os, re, sys
from flow import Stop, adventure, battle, find, lone_hero, main, ocr, tap_text, tap_wait, wait

HERE = os.path.dirname(os.path.abspath(__file__))


def tickets():
    return next((int(t) for x, y, w, h, t in ocr() if y < 120 and x < 300 and t.strip().isdigit()), None)


def claim_tower():
    """Treasure Chest Level reached ("Claim Reward", Remaining floor(s): 0): free claim -> Congratulations -> the next
    floors open with Challenge (Chien Than Floor 2030 -> 2031, 2026-11-03). Was skipped, which cost the Daily Mission
    "Challenged the Tower" row (150/160)."""
    tap_text(r'^Claim Reward$', (0, 1600, 1080, 1920)); wait(r'Congratulations|Tap anywhere', 8); tap_wait(540, 120)
    wait(r'^Challenge$', 10, (0, 1600, 1080, 1920)); print('tower: chest level -> Claim Reward claimed', flush=True)


def run(account, mode):
    cfg = open(os.path.join(HERE, '..', 'accounts', account + '.yaml')).read()
    if mode == 'tower':
        n = int(re.search(r'tower_of_the_throne:\s*(\d+)', cfg).group(1))
        adventure(r'Tower of the Throne'); boxes = wait(r'^Challenge$|^Claim Reward$', 10, (0, 1600, 1080, 1920))
        if not find(boxes, r'^Challenge$', (0, 1600, 1080, 1920)): claim_tower()
        for i in range(n):
            t = tickets()
            if t == 0: print('tower: 0 tickets left'); break
            res = battle(r'Tower of the Throne', timeout=150, setup=lone_hero if i == 0 else None)   # lineup sticks
            t2 = tickets()
            won = 'Victory' in res                         # a win costs no ticket (Chien Than 9 -> 9 at Floor 2020, 2026-11-01)
            if t is not None and t2 != t - 1 and not (won and t2 == t): raise Stop(f'tower tickets {t} -> {t2} after a fight')
            print(f'tower {i + 1}/{n}: {"Victory" if won else "Defeat" if "Defeat" in res else "?"}, tickets {t2}', flush=True)
            if find(ocr(), r'^Claim Reward$', (0, 1600, 1080, 1920)): claim_tower()
    elif mode == 'beast':
        adventure(r'Beast Realm'); wait(r'Next Beast', 10)
        res = battle(r'Next Beast', timeout=150)
        print(f'beast realm: 1 challenge done ({res[:60]})')
    else: raise Stop(f'unknown mode {mode}')


if __name__ == '__main__':
    main(run, sys.argv[1], sys.argv[2])
