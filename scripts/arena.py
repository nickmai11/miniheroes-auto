#!/usr/bin/env python3
# Arena: attack the topmost attackable opponent until tickets = 0 (ui-routine "Arena", steps 2-5).
# usage: D=<serial> scripts/arena.py <account>     e.g. scripts/arena.py cmajor   (Arena screen must be open)
# Reads the Challenge dialog with macOS Vision OCR (scripts/ocr): tickets "N/M", row names, blue Crash buttons.
# Attackable = any row (blue Crash or yellow Challenge, Nick 2026-11-04) whose name is not on accounts/tribe_<tribe>.txt (accounts/own_accounts.txt instead if arena.attack_tribemates: true, Mon-Wed game days only); else the last row (always a bot).
# skip_same_server accounts: last row (bot) only — the server tag isn't read. Never taps "+" or Refresh.
# A yellow Challenge is a real fight, taken only when the row's CP is below ours (Nick 2026-11-04; ours = the pinned own row at the
# bottom of the Arena ranking list): Start -> Victory/Defeat -> dismiss (UNTESTED, 2026-11-04). exit 0 = tickets 0 + dialog closed, 1 = unexpected screen (screenshot -> v_arena.png).
# Win chests / Ranking Rewards claims (step 6) stay with the helper.
# UNTESTED (written 2026-10-28 from saved screenshots) — run on one account first, watch it.
import datetime, difflib, os, re, subprocess, sys, time, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tap import grab, tap as tap_wait
from flow import Stop, find, joined, near, ocr, tap, tap_text, wait

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


cp_in = lambda boxes, region: [int(m[1]) for x, y, w, h, t in boxes if region[0] <= x <= region[2] and region[1] <= y <= region[3] for m in [re.fullmatch(r'(\d+)k', t.strip())] if m]   # 'NNNNk' fist numbers inside a device-coord region (x, y0, x1, y1) of box top-lefts


ZERO = str.maketrans('OoОо', '0000')  # Vision reads the ticket 0 as Latin/Cyrillic O (Bino 0/7, 2026-10-28); the max can read as Z (Aminor 0/7 -> О/Z, 2026-10-29)


def read_dialog():
    """(tickets, [(y, kind, name, cp)]) or None if the Challenge dialog isn't open. cp (k) sits left of the button, same height."""
    im = grab()
    if not near(im.getpixel((972, 188)), (255, 255, 255), 25): return None
    boxes = ocr(im)
    tix = next((int(m.group(1)) for x, y, w, h, t in boxes if x < 450 and 250 < y < 440
                for m in [re.search(r'(\d+)\s*\S?\s*/\s*\w', t.translate(ZERO))
                          or re.fullmatch(r'(\d+?)[01Il|](\d)', t.strip().translate(ZERO))] if m), None)   # 7/7 -> "707" (Bino/Dino 2026-10-29)
    if tix is None: return None
    rows = []
    for by, kind in buttons(im):
        names = [(y, t) for x, y, w, h, t in boxes if 250 <= x <= 700 and by - 140 <= y <= by - 25]
        cp = cp_in(boxes, (440, by - 50, 640, by + 30))
        rows.append((by, kind, min(names)[1] if names else '', cp[0] if cp else None))
    rows += [(y + h // 2, 'shield', '', None) for x, y, w, h, t in boxes if x > 700 and re.fullmatch(r'\d\d:\d\d:\d\d', t.strip())]  # crashed rows keep their place: the bot is the LAST row, not the last button (Bino 2026-11-06)
    return tix, sorted(rows, key=lambda r: r[0])


def stop(msg):
    grab().resize((540, 960)).save('v_arena.png'); print(msg + '; stop (screenshot v_arena.png)'); return 1


def main(account):
    cfg = open(os.path.join(HERE, '..', 'accounts', account + '.yaml')).read()
    tribe = re.search(r'arena:\s*\n\s+tribe:\s*(.+)', cfg).group(1).strip()
    bot_only = bool(re.search(r'skip_same_server:\s*true', cfg))
    # Dino/Bino/Dminor (attack_tribemates): tribemates fair game Mon-Wed game days only (Nick, 2026-11-06), never Nick's own accounts (Nick, 2026-11-04)
    game_day = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=5)).date()
    rfile = 'own_accounts.txt' if re.search(r'attack_tribemates:\s*true', cfg) and game_day.weekday() <= 2 else f'tribe_{tribe.lower().replace(" ", "_")}.txt'
    print(f'roster {rfile}', flush=True)
    roster = [norm(l) for l in open(os.path.join(HERE, '..', 'accounts', rfile)) if l.strip() and not l.startswith('#')]
    ours = cp_in(ocr(), (500, 1340, 800, 1480))     # own pinned row above the Challenge button (Cmajor 11-04: 6338k at (614,1414))
    ours = ours[0] if ours else None
    print(f'our CP {ours}k' if ours else 'our CP unreadable: Crash rows only', flush=True)
    ok = lambda k, cp: k == 'crash' or (ours is not None and cp is not None and cp < ours)   # Challenge only below our CP (Nick 2026-11-04)
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
        # topmost row: Crash, or Challenge below our CP — no Crash preference (Nick, 2026-11-04)
        pick = None if bot_only else next(((y, f'{nm} {cp}k', k) for y, k, nm, cp in rows[:-1] if ok(k, cp) and not tribemate(nm, roster)), None)
        if not pick:  # the last row (bot) can be cut off (Dino: 6 rows; Bino 2026-11-06: 4 shields hid a Crash bot) -> always scroll to the bottom first
            subprocess.run(['adb', '-s', D, 'shell', 'input', 'swipe', '540', '1500', '540', '900', '500']); time.sleep(1)
            d = read_dialog(); rows = d[1] if d else []
            if not rows: return stop('no last row (bot) found')
            if rows[-1][1] == 'shield': return stop('last row (bot) already crashed (shielded); nothing attackable')
            if not ok(rows[-1][1], rows[-1][3]): return stop(f'last row (bot) is a Challenge at {rows[-1][3]}k, not below our {ours}k')
            pick = (rows[-1][0], f'{rows[-1][2]} {rows[-1][3]}k (last row)', rows[-1][1])
        print(f'tickets {tix}: {pick[2]} {pick[1]!r}', flush=True)
        tap(866, pick[0]); time.sleep(2)
        if pick[2] == 'challenge':  # real fight (same screens as flow.battle): lineup Start -> result -> fall through to the dismiss loop
            try:
                b = wait(r'^Start$', 10); tap_text(r'^Start$', (0, 1650, 1080, 1920), b)
                for _ in range(2):  # Start tap can be lost (Bino 2026-11-05: lineup still up 180 s later) -> re-tap, at most twice
                    time.sleep(3); b = ocr()
                    if not (find(b, r'^Start$') and find(b, r'Quick Deploy')): break
                    print('  Start did not register; tapping again', flush=True); tap_text(r'^Start$', (0, 1650, 1080, 1920), b)
                r = joined(wait(r'Tap anywhere', 180)); print(f'  {"Victory" if "Victory" in r else "Defeat"}', flush=True)
            except Stop as e: return stop(f'challenge fight: {e}')
        t0 = time.time()
        while time.time() - t0 < 15 and not read_dialog():  # Congratulations -> dismiss -> reopen Challenge
            tap(540, 120); time.sleep(1.2)
            if read_dialog(): break
            tap(540, 1594); time.sleep(1.5)
        last, n = tix, n + 1
    return stop('20 rounds without reaching 0 tickets')


if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
