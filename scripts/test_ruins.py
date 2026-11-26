#!/usr/bin/env python3
# Offline check of ruins.py's hex grid + path choice. usage: python3 scripts/test_ruins.py
import os, sys
os.environ.setdefault('D', 'test')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ruins import DARK, LIGHT, centre, cols, kind, neighbours, path, step, ROWS

# neighbours are the 6 tiles one tile-width away (170 px in a row, 85 px / 127 px diagonally), and symmetric
for r in range(ROWS):
    for k in range(cols(r)):
        for n in neighbours(r, k):
            (x0, y0), (x1, y1) = centre(r, k), centre(*n)
            assert (abs(x0 - x1), abs(y0 - y1)) in ((170, 0), (80, 126), (80, 127), (90, 126), (90, 127)), ((r, k), n)
            assert (r, k) in neighbours(*n)
assert len(list(neighbours(4, 2))) == 6
# Cmajor floor 1 (2026-11-26): start (0,2) explored, its 4 neighbours explorable, door at row 7 col 5
grid = {(r, k): DARK for r in range(1, 9) for k in range(cols(r))}
grid.update({t: LIGHT for t in ((0, 1), (0, 3), (1, 2), (1, 3))})
assert step(grid, (7, 5)) in ((1, 2), (1, 3)), step(grid, (7, 5))   # either upper tile: both 6 tiles from the door
del grid[(1, 3)]; grid.update({(2, 2): LIGHT, (2, 3): LIGHT, (1, 4): LIGHT})   # (1,3) explored
assert step(grid, (7, 5)) in ((2, 2), (2, 3))                     # one row closer, not the sideways (1,4)
del grid[(2, 3)]                                                  # a roadblock there: not in the grid -> go round
assert step(grid, (7, 5)) in ((1, 4), (2, 2))
grid2 = {(7, 5): LIGHT}; assert step(grid2, (7, 5)) == (7, 5)     # door tile itself explorable -> tap it
assert step({(7, 5): DARK}, (7, 5)) is None                       # walled in -> no path
# tile colours measured on Cmajor (forest) and Tiger (ice) 2026-11-26
for c, want in (((42, 69, 41), DARK), ((108, 170, 100), LIGHT), ((25, 49, 74), DARK), ((25, 45, 66), DARK), ((66, 116, 178), LIGHT),
                ((41, 45, 41), None), ((49, 45, 41), None), ((16, 24, 25), None), ((73, 77, 83), None), ((130, 87, 48), None)):
    assert kind(c) == want, (c, kind(c))
# dark themes (Amethyst Cavern, Divine Battleground - Kratos / Kong 2026-11-26): read with the dark regime's cut
for c, want in (((16, 24, 41), DARK), ((49, 61, 99), LIGHT), ((33, 32, 41), DARK), ((90, 77, 107), LIGHT), ((41, 45, 41), None)):
    assert kind(c, 70) == want, (c, kind(c, 70))
# path(): the stamina to the target, and what burning a roadblock saves. Dminor floor 3: a corridor (col 2) up to the
# chest at row 10, a roadblock on (8,2); explorable tiles line the corridor up to row 7
grid = {(r, k): DARK for r in range(ROWS) for k in range(cols(r))}
for r in range(0, 8): del grid[(r, 2)]                            # the corridor, explored
del grid[(8, 2)]                                                  # the roadblock: not ground
for r in range(0, 9):
    for k in (1, 3): grid[(r, k)] = LIGHT
assert path(grid, (10, 2))[0] == 3, path(grid, (10, 2))           # round the roadblock: (8,1) -> (9,2) -> the chest
assert path(grid, (10, 2), [(8, 2)])[0] == 2, path(grid, (10, 2), [(8, 2)])   # burnt: (9,2) -> the chest
assert path({(7, 5): DARK}, (7, 5)) == (None, None) and path({(7, 5): DARK}, (7, 5), [(6, 4)])[0] == 1   # walled in -> the burnt neighbour opens it
print('ok')
