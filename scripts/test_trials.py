#!/usr/bin/env python3
# Offline check of trials.dungeon() against a fake game (no device). usage: python3 scripts/test_trials.py
import os, sys
os.environ.setdefault('D', 'test')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trials


class Game:
    def __init__(s, free, bought, buy_max): s.free, s.bought, s.buy_max, s.tip, s.spent, s.dialog, s.tips = free, bought, buy_max, False, [], True, 0
    def counter(s):
        if not s.dialog: return None
        return ('free', s.free) if s.free else ('buy', s.buy_max - s.bought)
    def text(s): return f'Spend {80 * (s.bought + 1)} diamonds' if s.tip else ''
    def tap_wait(s, x, y):
        if (x, y) == (540, 1372) and not s.free: s.tip = True; s.tips += 1
        elif (x, y) == (540, 1162) and s.tip: s.tip = False; s.spent.append(80 * (s.bought + 1)); s.bought += 1; s.free = 1
        elif (x, y) == (540, 120): s.tip = False
        elif (x, y) == (972, 572): s.dialog = False
    def sweep(s): assert s.free > 0 and not s.tip; s.free -= 1


def run(free, bought, buy_max, target):
    g = Game(free, bought, buy_max)
    trials.counter, trials.text, trials.tap_wait, trials.sweep_and_dismiss = g.counter, g.text, g.tap_wait, g.sweep
    trials.time.sleep = lambda s: None
    trials.button_price = lambda: 80 * (g.bought + 1)   # price on the Sweep button (buy mode)
    trials.dungeon('x', target)
    run.tips = g.tips
    return g.spent, 2 - g.free + g.bought if not g.free else None


assert run(2, 0, 5, 2)[0] == []                 # free only
assert run(2, 0, 4, 3)[0] == [80]               # Tiger: buy max 4, one paid
assert run(2, 0, 5, 4)[0] == [80, 160]          # config 160 = 4 sweeps
assert run(2, 0, 5, 5)[0] == [80, 160, 240]     # Kong gem_mine 240 = 5 sweeps (no per-sweep cap since 11-12)
assert run(0, 1, 5, 3)[0] == []                 # rerun: already 2 free + 1 paid today -> nothing
assert run(1, 0, 5, 3)[0] == [80]               # rerun mid-way
assert run(2, 0, 5, 1)[0] == []                 # config below free count
run(2, 0, 5, 3); assert run.tips == 1         # target reached: no extra Tip peek for the next price
run(2, 0, 5, 2); assert run.tips == 0
print('test_trials ok')
