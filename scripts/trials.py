#!/usr/bin/env python3
# Land of Trials: sweep each dungeon up to the account's configured total (free first, then paid within the cap).
# usage: D=<serial> scripts/trials.py <account>     (Land of Trials list screen must be open)
# Counters and prices are read with OCR (scripts/ocr) before and after every sweep:
#   dialog "Challenge Attempts: N" = free/bought left, "Remaining Purchase Attempts: N" = purchases left (max 5),
#   Tip popup "Spend P diamonds ..." = the price, checked against safety.max_gem_price_per_sweep before Confirm.
# Done today = 2 - free left, or 2 + purchases made (price ladder 80/160/240 -> 0/1/2 made; the purchase
# max differs per account: Tiger had 4, Cmajor 5).
# English UI only (keywords) — on a Vietnamese screen it stops with exit 1. "Match tickets full" popup: Confirm,
# keep going, print MATCH_FULL at the end. exit 0 = all dungeons handled, 1 = unexpected screen (v_trials.png).
# UNTESTED (written 2026-10-28 from saved screenshots) — run on one account first, watch it.
import os, re, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tap import grab, tap as tap_wait
from flow import ocr, tap

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.environ['D']
FREE_MAX = 2
# (config key, list half, GO tap) — device coords from ui-routine "ADB alternative"
DUNGEONS = [('abandoned_mine', 'top', (870, 540)), ('ancient_battlefield', 'top', (870, 925)),
            ('mysterious_forest', 'bottom', (870, 1016)), ('moonlight_temple', 'bottom', (870, 1402)),
            ('gem_mine', 'bottom', (870, 1786))]
match_full = False


class Stop(Exception): pass


def text():
    """OCR the screen; closes the 'Match tickets full' popup if it is up."""
    global match_full
    t = ' | '.join(b[4] for b in ocr(grab()))
    if 'reached the' in t and 'max' in t:
        match_full = True; tap_wait(720, 1162); t = ' | '.join(b[4] for b in ocr(grab()))
    return t


def counter():
    """('free', N) / ('buy', N) from the open sweep dialog, or None."""
    for _ in range(3):
        t = text()
        m = re.search(r'Purchase A\w*\W*(\d+)', t)
        if m: return 'buy', int(m.group(1))
        m = re.search(r'Challenge A\w*\W*(\d+)', t)
        if m: return 'free', int(m.group(1))
        time.sleep(1)
    return None


def sweep_and_dismiss():
    tap(540, 1372); time.sleep(7.5); tap(540, 700); time.sleep(1.5)  # reward popup auto-closes ~3 s; dismiss once


def dungeon(key, target, cap):
    c = counter()
    if not c: raise Stop(f'{key}: sweep dialog not readable')
    done = FREE_MAX - c[1] if c[0] == 'free' else FREE_MAX  # buy mode: paid count comes from the Tip price below
    runs, paid = 0, []
    while True:
        if c[0] == 'buy':
            if c[1] == 0: print(f'{key}: no purchases left'); break
            tap_wait(540, 1372)                       # Sweep -> Tip popup (nothing bought yet)
            m = re.search(r'Spend (\d+)', text())
            if not m: raise Stop(f'{key}: Tip popup price not readable')
            price = int(m.group(1))
            if price % 80: raise Stop(f'{key}: price {price} is not on the 80/160/240 ladder')
            done = FREE_MAX + price // 80 - 1          # purchases already made today
            if done >= target or price > cap:
                tap_wait(540, 120)
                if done < target: print(f'{key}: next sweep costs {price} > cap {cap}; stopped')
                break
            tap_wait(540, 1162); time.sleep(1.5)      # Confirm = buy 1 attempt
            if counter() != ('free', 1): raise Stop(f'{key}: after buying, dialog does not show Challenge Attempts: 1')
            paid.append(price); expect = lambda n, left=c[1]: n == ('buy', left - 1)
        else:
            if done >= target: break
            expect = (lambda n, left=c[1]: n == ('free', left - 1)) if c[1] > 1 else (lambda n: bool(n) and n[0] == 'buy')
        sweep_and_dismiss()
        new = counter()
        if not expect(new): raise Stop(f'{key}: counter {c} -> {new} after a sweep')
        c, done, runs = new, done + 1, runs + 1
    tap_wait(972, 572)
    if counter(): tap_wait(972, 572)                  # ✕ sometimes needs a second tap
    print(f'{key}: {done}/{target} done today ({runs} this run' + (f', paid {paid}' if paid else '') + ')', flush=True)


def main(account):
    cfg = open(os.path.join(HERE, '..', 'accounts', account + '.yaml')).read()
    cap = int(re.search(r'max_gem_price_per_sweep:\s*(\d+)', cfg).group(1))
    block = re.search(r'land_of_trials:\s*\n((?:\s+\w+:\s*\d+.*\n)+)', cfg).group(1)
    targets = {k: int(v) for k, v in re.findall(r'(\w+):\s*(\d+)', block)}
    if 'GO' not in text(): print('not on the Land of Trials list; stop'); return 1
    half = None
    try:
        for key, h, (x, y) in DUNGEONS:
            if not targets.get(key): continue
            if h != half:
                y0, y1 = ('500', '1500') if h == 'top' else ('1600', '400')
                subprocess.run(['adb', '-s', D, 'shell', 'input', 'swipe', '540', y0, '540', y1, '500']); time.sleep(1); half = h
            tap_wait(x, y); time.sleep(1.5)           # dialog must settle or the Sweep tap is lost
            dungeon(key, targets[key], cap)
    except Stop as e:
        grab().resize((540, 960)).save('v_trials.png'); print(f'{e}; stop (screenshot v_trials.png)'); return 1
    finally:
        if match_full: print('MATCH_FULL: tickets-full popup seen — run Match next')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
