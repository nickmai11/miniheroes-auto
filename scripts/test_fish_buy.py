#!/usr/bin/env python3
# Offline check of daily.refresh_row(): one scroll pack per empty count, used before the next; a pack that gives no
# refresh stops (Boudior 2026-11-14 bought 6 packs in 70 s). usage: python3 scripts/test_fish_buy.py
import os, sys
os.environ.setdefault('D', 'test')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import daily


def run(outputs):
    """fish_orders last lines in order -> (packs bought, Stop message or None)."""
    out, bought = iter(outputs), []
    daily.script = lambda *a: next(out)
    daily.buy_scrolls = lambda: bought.append(50) or 50
    try: return daily.refresh_row(1, '3'), None
    except daily.Stop as e: return (len(bought), sum(bought)), str(e)


assert run(['3 3']) == ((0, 0), None)                                   # good order: no refresh, no buy
assert run(['NOSCROLL 0', '2 3']) == ((1, 50), None)                    # empty: 1 pack, refreshed to 3
assert run(['NOSCROLL 0', 'NOSCROLL 5', '1 4']) == ((2, 100), None)    # pack used up (5 refreshes) -> 1 more pack
packs, err = run(['NOSCROLL 0', 'NOSCROLL 0', 'NOSCROLL 0'])           # pack gave no refresh (popup stuck open)
assert packs == (1, 50) and 'no refresh after buying' in err, (packs, err)
packs, err = run(['NOSCROLL 0', '0 None'])                              # unreadable after the buy: stop buying
assert packs == (1, 50) and err is None, (packs, err)
print('ok')
