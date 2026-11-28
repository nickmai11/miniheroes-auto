#!/usr/bin/env python3
"""Event hub -> Rune Salvage (mapped on pawn1 + Knight I 2026-11-20): disassemble Mythic runes with Select All (Nick
2026-11-20) until the event's 60 cap or no rune left, then claim the milestone chests (10/20/30/45/60, free).
Select All picks at most 20 per batch ("Selected: 20/20"); "Selected: 0/0" = nothing left to disassemble.
Each batch: Select All -> the Tip's count must equal the selection -> Confirm -> the Disassembled counter must go up.
usage: D=<serial> scripts/rune_salvage.py <account>   from the main screen."""
import re, sys, time
from flow import Stop, find, home, joined, main, tap_wait, wait
from daily import close_reward, hub_tabs, red_dot

MILESTONES = (276, 444, 608, 780, 948)          # chest icons 10/20/30/45/60, y 732; red dot ~56 px right, y ~676


def log(s): print(s, flush=True)


def state():
    """(disassembled, selected, selectable) from the screen."""
    b = wait(r'^Selected: \d+/\d+', 8)
    sel, cap = map(int, re.search(r'(\d+)/(\d+)', next(t for *_, t in b if t.startswith('Selected:')))[0].split('/'))
    # ponytail: OCR never reads the badge's lone "0" (7 accounts 2026-11-20, upscaled crop too) -> unreadable = 0; safe,
    # since a batch must then show a readable 20/40/60 or the loop guard stops
    n = next((int(t) for x, y, w, h, t in b if re.fullmatch(r'\d+', t.strip()) and x < 200 and 700 < y + h // 2 < 800), 0)
    return n, sel, cap


def run(acct):
    tap_wait(896, 340); wait(r'Match|Weekly', 10, (0, 1760, 1080, 1920)); time.sleep(1.5)
    x = hub_tabs().get('rune_salvage')
    if not x: log('SKIP no Rune Salvage event'); home(); return
    tap_wait(x, 1840); wait(r'Mythic Runes Owned', 8)
    for _ in range(4):                                         # 60 cap / 20 per batch = 3, +1 to read the 0/0
        n, sel, cap = state()
        if cap == 0: break
        tap_wait(332, 1638)                                    # Select All
        b = wait(r'^Selected: [1-9]', 5)
        k = int(re.search(r'Selected: (\d+)', joined(b))[1])
        tap_wait(748, 1638)                                    # Disassemble
        b = wait(r'Confirm disassembly', 5)
        m = re.search(r'selected (\d+) Mythic', joined(b))
        if not m or int(m[1]) != k: raise Stop(f'Tip count != selected {k}: {joined(b)[:200]}')
        tap_wait(*find(b, r'^Confirm$'))
        close_reward(dismiss=(540, 120))
        n2 = state()[0]
        if n2 <= n: raise Stop(f'Disassembled stayed {n} after a confirmed batch of {k}')   # loop guard
        log(f'disassembled {k} -> {n2}')
    else: raise Stop('still runes selectable after 3 batches (60 cap)')
    got = []
    for i, mx in enumerate(MILESTONES):
        if red_dot(mx + 30, 650, mx + 85, 700):
            tap_wait(mx, 732); close_reward(dismiss=(540, 120)); got.append((10, 20, 30, 45, 60)[i])
    log(f'DONE disassembled {state()[0]}/60, milestones claimed {got or "none"}')
    if not home(): raise Stop('lost the main screen after Rune Salvage')


if __name__ == '__main__':
    if len(sys.argv) < 2: sys.exit(__doc__)
    main(run, sys.argv[1])
