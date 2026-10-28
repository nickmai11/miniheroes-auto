#!/usr/bin/env python3
# Arena: crash the topmost attackable opponent until tickets = 0 (ui-routine "Arena", steps 2-5).
# usage: D=<serial> scripts/arena.py <account>     e.g. scripts/arena.py cmajor   (Arena screen must be open)
# Reads the Challenge dialog with macOS Vision OCR (scripts/ocr): tickets "N/M", row names, blue Crash buttons.
# Attackable = blue Crash + name not on accounts/tribe_<tribe>.txt; else the last row (always a bot).
# skip_same_server accounts: last row (bot) only — the server tag isn't read. Never taps "+", Refresh or a
# yellow Challenge. exit 0 = tickets 0 + dialog closed, 1 = unexpected screen (screenshot -> v_arena.png).
# Win chests / Ranking Rewards claims (step 6) stay with the helper.
# UNTESTED (written 2026-10-28 from saved screenshots) — run on one account first, watch it.
import difflib, os, re, subprocess, sys, time, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tap import grab, tap as tap_wait
from flow import near, ocr, tap

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.environ['D']
def norm(s):
    s = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in s if c.isalnum()).lower()


def tribemate(name, roster):
    n = norm(name)
    if len(n) < 2: return True  # unreadable -> treat as tribemate (the bot row still gets used)
    for r in roster:
        if (len(r) >= 4 and (r in n or n in r)) or difflib.SequenceMatcher(None, n, r).ratio() >= 0.75:
            return True
    return False


def buttons(im):
    """[(y_center, 'crash'|'challenge')] from a scan down x=940 (right of the button text) of the dialog list."""
    runs = []  # [kind, y0, y1]; gaps <= 48 px (button text) are bridged
    for y in range(420, 1780, 4):
        p = im.getpixel((940, y))
        k = 'crash' if p[2] > 170 and p[0] < 100 else 'challenge' if p[0] > 220 and p[1] > 140 and p[2] < 100 else None
        if not k: continue
        if runs and runs[-1][0] == k and y - runs[-1][2] <= 48: runs[-1][2] = y
        else: runs.append([k, y, y])
    return [((a + b) // 2, k) for k, a, b in runs if b - a >= 40]


ZERO = str.maketrans('OoОо', '0000')  # Vision reads the ticket 0 as Latin/Cyrillic O (Bino 0/7, 2026-10-28); the max can read as Z (Aminor 0/7 -> О/Z, 2026-10-29)


def read_dialog():
    """(tickets, [(y, kind, name)]) or None if the Challenge dialog isn't open."""
    im = grab()
    if not near(im.getpixel((972, 188)), (255, 255, 255), 25): return None
    boxes = ocr(im)
    tix = next((int(m.group(1)) for x, y, w, h, t in boxes if x < 450 and 250 < y < 440
                for m in [re.search(r'(\d+)\s*\S?\s*/\s*\w', t.translate(ZERO))] if m), None)
    if tix is None: return None
    rows = []
    for by, kind in buttons(im):
        names = [(y, t) for x, y, w, h, t in boxes if 250 <= x <= 700 and by - 140 <= y <= by - 25]
        rows.append((by, kind, min(names)[1] if names else ''))
    return tix, rows


def stop(msg):
    grab().resize((540, 960)).save('v_arena.png'); print(msg + '; stop (screenshot v_arena.png)'); return 1


def main(account):
    cfg = open(os.path.join(HERE, '..', 'accounts', account + '.yaml')).read()
    tribe = re.search(r'arena:\s*\n\s+tribe:\s*(.+)', cfg).group(1).strip()
    bot_only = bool(re.search(r'skip_same_server:\s*true', cfg))
    roster = [norm(l) for l in open(os.path.join(HERE, '..', 'accounts', f'tribe_{tribe.lower().replace(" ", "_")}.txt'))
              if l.strip() and not l.startswith('#')]
    tap_wait(540, 1594)  # Arena -> Challenge
    last, n = None, 0
    while n < 20:
        d = None
        for _ in range(3):
            d = read_dialog()
            if d: break
            time.sleep(1)
        if not d: return stop('Challenge dialog not open / tickets unreadable')
        tix, rows = d
        if last is not None and tix >= last: return stop(f'tickets did not drop ({last} -> {tix})')
        if tix == 0:
            tap_wait(972, 188); print(f'tickets 0 after {n} crashes; dialog closed'); return 0
        if not rows: return stop('no opponent rows found')
        pick = None if bot_only else next(((y, nm) for y, k, nm in rows[:-1] if k == 'crash' and not tribemate(nm, roster)), None)
        if not pick:
            if rows[-1][0] > 1400 or rows[-1][1] != 'crash':  # a 6th row can be cut off (Dino: 6 rows, 2 shielded) -> scroll to the real last row (the bot)
                subprocess.run(['adb', '-s', D, 'shell', 'input', 'swipe', '540', '1500', '540', '900', '500']); time.sleep(1)
                d = read_dialog(); rows = d[1] if d else []
            if not rows or rows[-1][1] != 'crash': return stop('last row is not a blue Crash')
            pick = (rows[-1][0], rows[-1][2] + ' (last row)')
        print(f'tickets {tix}: crash {pick[1]!r}', flush=True)
        tap(866, pick[0]); time.sleep(2)
        t0 = time.time()
        while time.time() - t0 < 15 and not read_dialog():  # Congratulations -> dismiss -> reopen Challenge
            tap(540, 120); time.sleep(1.2)
            if read_dialog(): break
            tap(540, 1594); time.sleep(1.5)
        last, n = tix, n + 1
    return stop('20 rounds without reaching 0 tickets')


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
