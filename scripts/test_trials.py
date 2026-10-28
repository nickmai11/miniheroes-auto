#!/usr/bin/env python3
# Offline check of trials.dungeon() against a fake game (no device). usage: python3 scripts/test_trials.py
import os, sys
os.environ.setdefault('D', 'test')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import trials


class Game:
    def __init__(s, free, bought, buy_max): s.free, s.bought, s.buy_max, s.tip, s.spent, s.dialog = free, bought, buy_max, False, [], True
    def counter(s):
        if not s.dialog: return None
        return ('free', s.free) if s.free else ('buy', s.buy_max - s.bought)
    def text(s): return f'Spend {80 * (s.bought + 1)} diamonds' if s.tip else ''
    def tap_wait(s, x, y):
        if (x, y) == (540, 1372) and not s.free: s.tip = True
        elif (x, y) == (540, 1162) and s.tip: s.tip = False; s.spent.append(80 * (s.bought + 1)); s.bought += 1; s.free = 1
        elif (x, y) == (540, 120): s.tip = False
        elif (x, y) == (972, 572): s.dialog = False
    def sweep(s): assert s.free > 0 and not s.tip; s.free -= 1


def run(free, bought, buy_max, target, cap):
    g = Game(free, bought, buy_max)
    trials.counter, trials.text, trials.tap_wait, trials.sweep_and_dismiss = g.counter, g.text, g.tap_wait, g.sweep
    trials.time.sleep = lambda s: None
    trials.dungeon('x', target, cap)
    return g.spent, 2 - g.free + g.bought if not g.free else None


assert run(2, 0, 5, 2, 160)[0] == []                 # free only
assert run(2, 0, 4, 3, 160)[0] == [80]               # Tiger: buy max 4, one paid
assert run(2, 0, 5, 4, 160)[0] == [80, 160]          # cap 160 allows the 160 one
assert run(2, 0, 5, 5, 160)[0] == [80, 160]          # 240 > cap -> stop
assert run(0, 1, 5, 3, 160)[0] == []                 # rerun: already 2 free + 1 paid today -> nothing
assert run(1, 0, 5, 3, 160)[0] == [80]               # rerun mid-way
assert run(2, 0, 5, 1, 160)[0] == []                 # config below free count
print('test_trials ok')
