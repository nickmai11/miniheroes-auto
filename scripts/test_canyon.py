#!/usr/bin/env python3
# Offline check of canyon.season_left() / purple_enough() (Nick 2026-11-21: purple 9/m reaches 80k by season end ->
# stay purple, leave Gold). usage: python3 scripts/test_canyon.py
import datetime, os, sys
os.environ.setdefault('D', 'test')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
from canyon import foes, plate, purple_enough, season_left

utc = datetime.timezone.utc
sat = datetime.datetime(2026, 11, 21, 6, 0, tzinfo=utc)                  # Sat 13:00 local (+07)
assert season_left(sat) == 41 * 60                                       # -> Sun 23:00 UTC
assert season_left(datetime.datetime(2026, 11, 22, 22, 30, tzinfo=utc)) == 30
assert season_left(datetime.datetime(2026, 11, 23, 10, 0, tzinfo=utc)) == (6 * 24 + 13) * 60   # Mon 10:00 UTC: new season
assert season_left(datetime.datetime(2026, 11, 21, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(hours=7)))) == 41 * 60
assert purple_enough(79665, 60)                                          # Tiger 11-21: 80k in under an hour
assert purple_enough(80000, 0)                                           # already there
assert not purple_enough(50000, 60)
assert purple_enough(60000, 41 * 60)                                     # 60000 + 20295 (22 h a day) >= 80k
assert not purple_enough(61431, 2203)                                    # Gambler 11-21: 81258 at 24 h a day, 79606 at 22
assert purple_enough(61908, 2210)                                       # Bino 11-21: 80140 at 22 h a day
assert not purple_enough(None, 10000)                                    # points unreadable -> old rules
# highest (Nick 2026-11-24): blue plate = tribemate, green = own account -> skipped; any other plate = a foe
im = Image.new('RGB', (1080, 1920), (206, 154, 66))                      # sand
for x, c in ((200, (58, 125, 195)), (500, (0, 150, 16)), (800, (39, 84, 132))): im.paste(c, (x - 100, 422, x + 100, 458))
assert [plate(im, x, 500) for x in (200, 500, 800, 1000)] == ['blue', 'green', 'blue', None]
boxes = [(150, 485, 100, 30, '* 2960k'), (450, 485, 100, 30, '4374k'), (950, 485, 100, 30, '602K'), (20, 100, 80, 30, '9999k')]
assert foes(im, boxes) == [(1000, 364)]                                  # no plate above 602K; the header text isn't a spot
im.paste((64, 64, 144), (900, 822, 1080, 858))                           # Sentinel plate: slate, not tribe blue
assert foes(im, boxes + [(950, 885, 100, 30, '57918'), (150, 885, 100, 30, '5')]) == [(1000, 364), (1000, 764)]   # a Sentinel's CP has no 'k' (Tiger 2026-11-25)
print('ok')
