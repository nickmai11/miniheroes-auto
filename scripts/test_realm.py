#!/usr/bin/env python3
# Offline check of realm.climb() / best_core() / cp() (no device). usage: python3 scripts/test_realm.py
import os, sys
os.environ.setdefault('D', 'test')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from realm import best_core, climb, cp

TUE, THU = 1, 3
assert climb(1, 0, 2, 1, TUE) == 'map'      # F1, no bandit yet -> map, any day
assert climb(1, 1, 2, 1, TUE) == 'stay'     # F1, 1 bandit -> hunt the 2nd
assert climb(1, 0, 2, 0, TUE) == 'stay'     # no map
assert climb(1, 2, 2, 0, TUE) == 'kills'
assert climb(2, 0, 2, 5, TUE) == 'stay'     # F2 before Thu: 5 maps are the reserve
assert climb(2, 0, 2, 6, TUE) == 'map'      # a spare 6th map
assert climb(2, 1, 2, 6, TUE) == 'stay'     # 1 pilot down -> hunt, even with spares
assert climb(2, 0, 2, 1, THU) == 'map'      # Thursday: use the reserve
assert climb(2, 1, 2, 3, THU) == 'stay'
assert climb(2, 2, 2, 9, TUE) == 'kills'

row = lambda y, t: (200, y, 300, 40, t)
lair = [row(1064, '10y ATK Beast core'), row(1228, '1ky DEF Beast core'), row(1392, '1ky ATK Beast core')]
assert best_core(lair)[4] == '1ky ATK Beast core'                            # tier first, then ATK
assert best_core([row(1, '10y HP Beast core'), row(2, '10y DEF Beast core')])[4] == '10y DEF Beast core'
assert best_core([row(1, '10y ATK Beast core'), row(2, '1my ATK Beast core')]) is None   # unknown tier -> stop

assert cp('7177k') == 7177 and cp('2310K') == 2310 and cp('12.3M') == 12300 and cp('Lv.177') is None
print('ok')
