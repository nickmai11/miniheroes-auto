#!/usr/bin/env python3
# Tribe Clash battle: D=<serial> scripts/tc.py   (main screen or Tribe Clash screen; battle days 10:00-22:00 UTC)
# Enter -> battle map -> any castle on screen that is not ours (top-left box), not an ally (accounts/allies.txt, Nick
# 2026-11-10) and not Destroyed (Nick: "just pick one") -> Attack until Free Attempts 0. Never Siege Tokens (the counter
# turns into a token icon "held/cost" at 0 free attempts). Mapped on Cmajor 2026-11-10.
# Last: the Treasure keys (clash_treasure.py, Nick 2026-11-11). Ends on the main screen.
import os, re, time
import clash_treasure
from flow import Stop, find, grab, joined, main, near, ocr, swipe, tap_text, tap_wait, wait

HERE = os.path.dirname(os.path.abspath(__file__))
ALLIES = {l.strip() for l in open(os.path.join(HERE, '..', 'accounts', 'allies.txt')) if l.strip()[:1].isdigit()}
MOVES = [(540, 1400, 540, 500), (540, 500, 540, 1400), (540, 500, 540, 1400), (900, 900, 200, 900), (200, 900, 900, 900),
         (200, 900, 900, 900)]   # map is bigger than the screen: look around until a target shows


def target(b, own):
    for x, y, w, h, t in b:
        m = re.match(r'S(\d{1,3})\b', t)
        if not m or y < 520 or y > 1700 or m[1] == own or m[1] in ALLIES: continue   # y<520: building (90 px up) under our info box (Tiger 11-11 tapped it)
        near = [u for X, Y, W, H, u in b if abs(Y - y) < 140 and abs(X - x) < 300]
        if any('Destroyed' in u or re.fullmatch(r'0%', u) for u in near): continue
        return t, (x + w // 2, y - 90)                  # building sits ~90 px above its label


def run():
    b = ocr()
    if not find(b, r'will advance'):
        if not find(b, r'^Enter$'):
            tap_text(r'Tribe Clash', (680, 560, 1080, 680), b)         # main-screen banner
            b = wait(r'^Enter$', 15)
        tap_text(r'^Enter$', boxes=b); b = wait(r'will advance', 10)
    own = re.search(r'S(\d{1,3})', ' '.join(t for x, y, w, h, t in b if y < 160 and x < 500))
    if not own: raise Stop(f'own castle box unreadable: {joined(b)[:200]}')
    own = own[1]
    for mv in [None] + MOVES:
        if mv: swipe(*mv, 600); time.sleep(1); b = ocr()
        tg = target(b, own)
        if tg: break
    else: raise Stop(f'no attackable castle found (own S{own}): {joined(b)[:200]}')
    print(f'own S{own}, target {tg[0]}', flush=True)
    tap_wait(*tg[1]); b = wait(r'^Attack$|Free Attempts|^\d+/\d+$', 6)
    n = 0
    while True:
        c = re.search(r'Free Attempts: (\d+)/(\d+)', joined(b))
        if not c:
            print(f'free attempts 0 (Siege Tokens not used) - {n} attacks', flush=True); break
        if c[1] == '0': print(f'free attempts 0 - {n} attacks', flush=True); break
        tap_text(r'^Attack$', boxes=b)
        try: r = joined(wait(r'Tap anywhere', 8))
        except Stop:                                    # 11-11 round 1: 5/9 accounts' Attack tap didn't register
            b = ocr()
            if not find(b, r'^Attack$') or f'Free Attempts: {c[1]}/' not in joined(b): raise
            print(f'attack {n + 1}: no result in 8 s, counter still {c[1]} - tapping Attack again', flush=True)
            tap_text(r'^Attack$', boxes=b); r = joined(wait(r'Tap anywhere', 30))
        d = re.search(r'You dealt (\S+) damage', r); n += 1
        print(f'attack {n} ({c[1]}/{c[2]} before): {d[1] if d else r[:120]}', flush=True)
        tap_wait(540, 1700); b = wait(r'^Attack$', 8)
        if 'Free Attempts' in joined(b) and re.search(r'Free Attempts: (\d+)', joined(b))[1] == c[1]:
            raise Stop(f'counter did not drop after attack {n}: {joined(b)[:200]}')
    home()
    clash_treasure.run()                                 # last tc step: spend the Treasure keys (Nick 2026-11-11)
    home()


def home():
    for _ in range(4):                                   # attack screen -> map -> TC screen -> main
        tap_wait(92, 1810); time.sleep(0.5)
        if near(grab().getpixel((92, 1788)), (0, 158, 230)): return
    raise Stop('not back on the main screen')


main(run)
