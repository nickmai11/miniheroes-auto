#!/usr/bin/env python3
# Land of Trials: sweep each dungeon up to the account's configured total (free first, then paid within the cap).
# usage: D=<serial> scripts/trials.py <account>     (Land of Trials list screen must be open)
# Counters and prices are read with OCR (scripts/ocr) before and after every sweep:
#   dialog "Challenge Attempts: N" = free/bought left, "Remaining Purchase Attempts: N" = purchases left (max 5),
#   the gem price on the Sweep button itself (80 / 160 / 240) = the next purchase - read BEFORE tapping (Nick
#   2026-11-03: "if you have to click on the sweep and see this popup to know that you have reached the limit,
#   something is wrong"); the Tip popup "Spend P diamonds" is only the Confirm, its price must equal the button's.
# Done today = 2 - free left, or 2 + purchases made (price ladder 80/160/240 -> 0/1/2 made; the purchase
# max differs per account: Tiger had 4, Cmajor 5).
# Sweep the configured count and move on; safety.max_gem_price_per_sweep is only a safeguard (Nick, 2026-10-29/11-03).
# "Match tickets full" popup: flow.tickets_full spends them (Confirm -> arena.py), then exit 1 with MATCH_FULL so the
# runner redoes trials. exit 0 = all dungeons handled, 1 = unexpected screen (v_trials.png).
import os, re, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tap import grab, tap as tap_wait
from flow import Stop, find, ocr, tap, tickets_full

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.environ['D']
FREE_MAX = 2
# (config key, list half, GO tap) — device coords from ui-routine "ADB alternative"
DUNGEONS = [('abandoned_mine', 'top', (870, 540)), ('ancient_battlefield', 'top', (870, 925)),
            ('mysterious_forest', 'bottom', (870, 1016)), ('moonlight_temple', 'bottom', (870, 1402)),
            ('gem_mine', 'bottom', (870, 1786))]


def text():
    """OCR the screen; closes the 'Match tickets full' popup if it is up."""
    boxes = ocr(grab()); t = ' | '.join(b[4] for b in boxes)
    if tickets_full(boxes): raise Stop('MATCH_FULL: arena tickets spent, redo this step')
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


def button_price():
    """Gem price printed on the dialog's Sweep button (buy mode), or None."""
    for _ in range(3):
        boxes = ocr(grab())
        if find(boxes, r'^Sweep$', (300, 1320, 800, 1430)):
            p = [int(t) for x, y, w, h, t in boxes if 300 < x + w // 2 < 800 and 1320 < y + h // 2 < 1430 and t.strip().isdigit()]
            if p: return p[0]
        time.sleep(0.7)


def sweep_and_dismiss():
    tap(540, 1372); time.sleep(7.5); tap(540, 700); time.sleep(1.5)  # reward popup auto-closes ~3 s; dismiss once


def dungeon(key, target, cap):
    c = counter()
    if not c: raise Stop(f'{key}: sweep dialog not readable')
    done = FREE_MAX - c[1] if c[0] == 'free' else FREE_MAX  # buy mode: paid count comes from the Sweep button price below
    runs, paid = 0, []
    known = c[0] == 'free'                            # buy mode on entry: done today only readable from the next price
    while True:
        if known and done >= target: break            # target reached: never open the Tip just to see the next price (Nick)
        if c[0] == 'buy':
            if c[1] == 0: print(f'{key}: no purchases left'); break
            price = button_price()                    # read on the Sweep button - no tap to find it out
            if price is None: raise Stop(f'{key}: Sweep button price not readable')
            if price % 80: raise Stop(f'{key}: price {price} is not on the 80/160/240 ladder')
            done, known = FREE_MAX + price // 80 - 1, True   # purchases already made today
            if done >= target: break
            if price > cap: print(f'{key}: next sweep costs {price} > cap {cap} (safeguard); stopped'); break
            tap_wait(540, 1372)                       # Sweep -> Tip = the Confirm for this purchase
            m = re.search(r'Spend (\d+)', text())
            if not m or int(m.group(1)) != price:
                tap_wait(540, 120); raise Stop(f'{key}: Tip price {m and m.group(1)} != button price {price}')
            tap_wait(540, 1162); time.sleep(1.5)      # Confirm = buy 1 attempt
            if counter() != ('free', 1): raise Stop(f'{key}: after buying, dialog does not show Challenge Attempts: 1')
            paid.append(price); expect = lambda n, left=c[1]: n == ('buy', left - 1)
        else:
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
            for attempt in (1, 2):                    # the tickets-full popup can swallow the GO tap (Kong 2026-10-28)
                tap_wait(x, y); time.sleep(1.5)       # dialog must settle or the Sweep tap is lost
                if counter() or attempt == 2: break
            dungeon(key, targets[key], cap)
    except Stop as e:
        grab().resize((540, 960)).save('v_trials.png'); print(f'{e}; stop (screenshot v_trials.png)'); return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
