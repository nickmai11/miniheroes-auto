#!/usr/bin/env python3
# Poseidon's Ruins (Tribe): spend every Attack Attempt on the lowest-CP enemy ship with a red heart
# (ui-routine "Poseidon's Ruins", skill miniheroes-poseidon).
# usage: scripts/poseidon.py <serial> [<serial> ...]   one process per account, all in parallel
#        (or D=<serial> scripts/poseidon.py)            from the main screen, Tribe screen or the Ruins map
# Accounts in the same tribe share the enemy list: each fight takes a lock /tmp/miniheroes-poseidon/<ship>, so
# parallel accounts never hit the same ship at once — they spread to the next-lowest ship. Positions are read
# from the screen (OCR name + CP, red-heart pixels) every round, never fixed coords; the Plunder popup is
# re-checked (name + a red heart) before Attack. Never Contribute, never buys attempts, no gems.
# exit 0 = attempts 0 + back on the main screen, 1 = unexpected screen (screenshot v_poseidon.png; with serial args:
# /tmp/miniheroes-poseidon-out/<serial>/v_poseidon.png).
import difflib, os, re, shutil, subprocess, sys, time, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

LOCKS = '/tmp/miniheroes-poseidon'
CP = re.compile(r'^\D{0,2}(\d+(?:\.\d+)?)\s*([kKmM])$')  # "1657k"; boxes merged with other text are dropped


def norm(s): return ''.join(c for c in unicodedata.normalize('NFKD', s) if c.isalnum()).lower()


def is_red(p): return p[0] > 200 and p[1] < 40 and 45 < p[2] < 110  # heart (255,0,74); grey heart (175,190,215)


def reds(im, x0, y0, x1, y1):
    x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, im.width), min(y1, im.height)
    return sum(1 for y in range(y0, y1, 4) for x in range(x0, x1, 4) if is_red(im.getpixel((x, y))))


def ships(boxes, im):
    """[(cp, name, tap_x, tap_y, alive)] from the map: CP box, name box just above it, hearts 60-480 px above the name."""
    out = []
    for x, y, w, h, t in boxes:
        m = CP.match(t.strip())
        if not m or y < 220: continue
        cp = float(m.group(1)) * (1000 if m.group(2) in 'mM' else 1)
        above = [b for b in boxes if 0 < y - b[1] < 80 and abs(b[0] + b[2] / 2 - (x + w / 2)) < 120 and not CP.match(b[4].strip())]
        if not above: continue
        nx, ny, nw, nh, name = max(above, key=lambda b: b[1])
        cx, cy = nx + nw // 2, ny + nh // 2
        tx, ty = cx, cy - 140                     # the ship's hull
        if tx < 200 and ty < 700: continue        # behind Report / Rewards / Contribute
        if ty > 1700: continue                    # behind the Allies/Enemies bar
        out.append((cp, name, tx, ty, reds(im, cx - 80, cy - 480, cx + 80, cy - 60) >= 8))
    return out


def lock(name):
    p = os.path.join(LOCKS, norm(name) or 'unknown')
    os.makedirs(LOCKS, exist_ok=True)
    try:
        if time.time() - os.path.getmtime(p) > 90: shutil.rmtree(p, ignore_errors=True)  # stale (crashed run)
    except OSError: pass
    try: os.mkdir(p); return p
    except FileExistsError: return None


def run():
    from flow import Stop, find, grab, joined, ocr, swipe, tap, tap_text, tap_wait, wait
    is_main = lambda: all(abs(a - b) <= 40 for a, b in zip(grab().getpixel((92, 1788)), (0, 158, 230)))

    def attempts():
        for _ in range(3):
            boxes = ocr()
            a = find(boxes, r'Attack Attempts', (0, 100, 400, 220))
            if a:
                for x, y, w, h, t in boxes:
                    m = re.search(r'(\d+)\s*$', t)
                    if m and abs(y + h / 2 - a[1]) < 30 and x < 400: return int(m.group(1))
            time.sleep(0.7)
        raise Stop('Attack Attempts counter unreadable')

    # ---- navigate to the map ----
    if not find(ocr(), r'Attack Attempts'):
        if not find(ocr(), r"Poseidon"):
            if not is_main(): raise Stop('not on the main screen, Tribe screen or the Ruins map')
            for _ in range(2):  # first Tribe tap right after the main screen appears can be ignored
                tap_wait(448, 1780)
                try: wait(r'Poseidon', 6); break
                except Stop: pass
            else: raise Stop('Tribe screen did not open')
        tap_text(r'Poseidon')
        wait(r'Attack Attempts', 15)
    tap_text(r'^Enemies$', (540, 1700, 1080, 1920))

    n, busy, wins, losses = attempts(), set(), 0, 0
    print(f'attack attempts {n}', flush=True)
    while n > 0:
        for _ in range(3): swipe(540, 1500, 540, 700, 400)  # bottom = lowest CP
        time.sleep(0.8)
        pick = None
        for page in range(6):
            im = grab(); boxes = ocr(im)
            cands = sorted(s for s in ships(boxes, im) if s[4] and norm(s[1]) not in busy)
            for s in cands:
                lk = lock(s[1])
                if lk: pick = s + (lk,); break
                print(f'  {s[1]} ({s[0]:.0f}k) locked by another account, next', flush=True)
            if pick or page == 5: break
            swipe(540, 700, 540, 1500, 600); time.sleep(0.8)
        if not pick: raise Stop(f'no enemy ship with a red heart found ({n} attempts left)')
        cp, name, tx, ty, _, lk = pick
        try:
            tap(tx, ty)
            t0, popup = time.time(), None
            while time.time() - t0 < 4:
                boxes = ocr()
                if find(boxes, r'being challenged|was plundered'): break
                if find(boxes, r'^Plunder$') and find(boxes, r'^Attack$', (540, 1250, 1000, 1420)): popup = boxes; break
                time.sleep(0.4)
            if not popup:
                print(f'  {name}: no Plunder popup ({joined(boxes)[:80]}), next ship', flush=True)
                busy.add(norm(name)); time.sleep(1.5); continue  # let a toast fade
            names = [b[4] for b in popup if 400 < b[1] < 1100]
            if not any(difflib.SequenceMatcher(None, norm(name), norm(t)).ratio() >= 0.6 for t in names) \
                    or not reds(grab(), 90, 550, 290, 630):
                print(f'  popup is not {name} with a red heart ({" | ".join(names)}), cancel', flush=True)
                tap_wait(336, 1336); busy.add(norm(name)); continue
            print(f'attempt {n}: plunder {name} ({cp:.0f}k)', flush=True)
            tap_text(r'^Attack$', (540, 1250, 1000, 1420), popup)
            wait(r'^Start$', 10, (0, 1650, 1080, 1920))
            tap(540, 1808)
            t0, res = time.time(), None
            while time.time() - t0 < 60:
                time.sleep(1); boxes = ocr()
                if find(boxes, r'Tap anywhere to close'): res = joined(boxes); break
                if time.time() - t0 > 6 and find(boxes, r'^Start$', (0, 1650, 1080, 1920)):
                    break  # target sank while on the lineup: Start does nothing, no attempt lost
            if res is None:
                if not find(ocr(), r'^Start$', (0, 1650, 1080, 1920)): raise Stop('no result screen after Start')
                print(f'  {name}: Start did nothing (sunk / being attacked), back', flush=True)
                tap_wait(84, 1810); wait(r'Attack Attempts', 10); busy.add(norm(name)); continue
            win = 'Victory' in res
            wins, losses = wins + win, losses + (not win)
            tap(540, 1880)  # dismiss low: (540,1700) can land on a ship once the result closes
            wait(r'Attack Attempts', 10)
        finally:
            shutil.rmtree(lk, ignore_errors=True)
        left = attempts()
        print(f'  {"Victory" if win else "Defeat"} vs {name}; attempts {n} -> {left}', flush=True)
        if left != n - 1: raise Stop(f'attempts did not drop by 1 ({n} -> {left})')
        n = left

    for _ in range(4):  # map -> Tribe -> main (a late back can open Recruit: back again)
        if is_main(): break
        tap_wait(92, 1810); time.sleep(0.8)
    else: raise Stop('could not get back to the main screen')
    print(f'attempts 0: {wins} wins, {losses} losses; back on main', flush=True)


if __name__ == '__main__':
    if len(sys.argv) > 1:  # parent: one child per serial, output prefixed with the serial
        procs = []
        for s in sys.argv[1:]:  # own cwd each, so v_poseidon.png screenshots don't overwrite each other
            cwd = os.path.join(LOCKS + '-out', s.replace(':', '_')); os.makedirs(cwd, exist_ok=True)
            procs.append((s, subprocess.Popen([sys.executable, os.path.abspath(__file__)], env={**os.environ, 'D': s}, cwd=cwd,
                                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)))
        import threading
        def pump(s, p):
            for line in p.stdout: print(f'[{s}] {line}', end='', flush=True)
        ts = [threading.Thread(target=pump, args=sp) for sp in procs]
        for t in ts: t.start()
        for t in ts: t.join()
        sys.exit(max(p.wait() for _, p in procs))
    from flow import main
    main(run)
