#!/usr/bin/env python3
# Offline check of canyon.season_left() / purple_enough() (Nick 2026-11-21: purple 9/m reaches 80k by season end ->
# stay purple, leave Gold). usage: python3 scripts/test_canyon.py
import datetime, os, sys
os.environ.setdefault('D', 'test')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from canyon import purple_enough, season_left

utc = datetime.timezone.utc
sat = datetime.datetime(2026, 11, 21, 6, 0, tzinfo=utc)                  # Sat 13:00 local (+07)
assert season_left(sat) == 41 * 60                                       # -> Sun 23:00 UTC
assert season_left(datetime.datetime(2026, 11, 22, 22, 30, tzinfo=utc)) == 30
assert season_left(datetime.datetime(2026, 11, 23, 10, 0, tzinfo=utc)) == (6 * 24 + 13) * 60   # Mon 10:00 UTC: new season
assert season_left(datetime.datetime(2026, 11, 21, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=7)))) == 41 * 60
assert purple_enough(79665, 60)                                          # Tiger 11-21: 80k in under an hour
assert purple_enough(80000, 0)                                           # already there
assert not purple_enough(50000, 60)
assert purple_enough(58000, 41 * 60)                                     # 58000 + 22140 >= 80k
assert not purple_enough(None, 10000)                                    # points unreadable -> old rules
print('ok')
