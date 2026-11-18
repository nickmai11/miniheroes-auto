#!/usr/bin/env python3
# Offline check of daily.preferred(): cut owned-row names as OCR'd in the logs (Tiger 2026-11-18 lost ATK Drill and
# Concentrated Fire to non-preferred offers). usage: python3 scripts/test_bonus_pick.py
import os, sys
os.environ.setdefault('D', 'test')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from daily import preferred, score

for n in ['ATK Drill', 'ATK DI', 'ATK', 'DMG Increase Drill', 'DMG Incr', 'Concentr Fire', 'Concentrated Fire', 'Iron Shi',
          'Mental', 'Mental Fear', 'Infinite', 'Infinite Energy', 'Battle Cry', 'Battle']:
    assert preferred(n), n
for n in ['Weakening Strike', 'Weaken Strik', 'Judgment Moment', 'Judgm Mome', 'Stun Cu', 'DMG Red', 'DMG Reduction',
          'Full RES', 'FulI', 'Heroic', 'Battle Spirit', 'Battle Ble', 'Armor PEN', 'RES Blessing', 'Team Friendship', '?']:
    assert not preferred(n), n
# replace decision = score(best offer) > score(weakest owned); card = (x, rarity 0 Rare..3 Mythic, name)
assert score((0, 3, 'ATK Drill')) > score((0, 2, 'Iron Shi'))          # Mythic preferred over Legend preferred
assert not score((0, 2, 'ATK Drill')) > score((0, 2, 'Concentr Fire'))  # same rarity: keep
assert not score((0, 3, 'Stun Curse')) > score((0, 1, 'ATK DI'))        # non-preferred never over preferred
assert score((0, 1, 'Mental Fear')) > score((0, 3, 'Judgm Mome'))       # preferred over non-preferred
print('ok')
