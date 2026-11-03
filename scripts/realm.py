#!/usr/bin/env python3
# Floating Realm (Tribe cross-server event, every 2 weeks; battle Tue/Wed/Thu 10:00-22:00 UTC): spend all stamina
# exploring. Rules: docs/ui-routine.md "Floating Realm" (Nick, 2026-11-03).
# usage: D=<serial> scripts/realm.py <account>      (main screen or the explore screen; ends on the main screen)
# Treasure -> Claim, weak monster -> Crush, monster/player -> Attack whatever the CP, Defeat -> Mark (Nick), Monster Lair -> stake
# the best core, next floor -> kills or a Treasure Map (map strategy). Anything else -> exit 1 (v_realm.png).
# Never taps the stamina "+" (gems). UNTESTED end-to-end (written 2026-11-03 from Kong's first run) - watch it.
import datetime, os, re, sys, time
from flow import Stop, find, grab, joined, main, near, ocr, tap_text, tap_wait, wait

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
RESERVE = 5       # Treasure Maps kept for Thursday's F2->F3 re-entries
FLOORS = {'Nagrand': 1, 'Land of Blaze': 2, 'Floating Castle': 3}
TIER = {'y': 1, 'ky': 1000}                # beast cores seen: 10y (blue), 1ky (orange)
STAT = {'ATK': 0, 'DEF': 1, 'HP': 2}       # same tier: ATK -> DEF -> HP (Nick)
NOW = datetime.datetime.now(datetime.timezone.utc)
LOG = None


def say(msg):
    line = f'{time.strftime("%F %T")} [realm] {msg}'
    print(line, flush=True)
    if LOG: open(LOG, 'a').write(line + '\n')


def battle_on():
    """Battle rounds: Tue/Wed/Thu 10:00-22:00 UTC of every 2nd week (first seen Tue 2026-11-03)."""
    return (NOW.date() - datetime.date(2026, 11, 3)).days % 14 < 3 and 10 <= NOW.hour < 22


def cp(t):
    """'7177k' / '2310K' / '12.3M' -> thousands, else None."""
    m = re.fullmatch(r'(\d+(?:\.\d+)?)([kKmM])', t.strip())
    return m and float(m[1]) * (1000 if m[2] in 'mM' else 1)


def cps(b, y0, y1): return [v for x, y, w, h, t in b if y0 < y + h // 2 < y1 and (v := cp(t))]


def floor(b):
    t = ' '.join(x[4] for x in b if x[0] > 760 and x[1] < 300)    # top-right floor card label
    return next((n for k, n in FLOORS.items() if k in t), None)


def fight(b, title):
    """Monster/player dialog with Attack: always attack, CP doesn't matter; a Defeat is Marked (Nick, 2026-11-03)."""
    foe = cps(b, 540, 640)
    tap_text(r'^Attack$', (0, 1150, 1080, 1400), b)
    b = wait(r'^Start$', 10)
    # our CP (top left) '0' = empty lineup the first time. OCR reads the fist icon as a 1st char ('Z9100K', '27519K')
    deployed = lambda b: any(re.search(r'[1-9]\d*K$', x[4], re.I) for x in b if x[0] < 540 and 40 < x[1] < 140)
    if not deployed(b):
        tap_text(r'Quick Deploy', boxes=b); b = wait(r'^Start$', 5)
        if not deployed(b): raise Stop('lineup still empty after Quick Deploy')
    tap_text(r'^Start$', (0, 1650, 1080, 1920), b)
    r = joined(wait(r'Tap anywhere', 150))
    won = 'Victory' in r
    say(f'  attack {title} {foe}k: {"Victory" if won else "Defeat"}, {r[r.find("Rewards"):r.find("Confirm")]}')
    c = find(ocr(), r'^Confirm$'); tap_wait(*(c or (540, 1700)))
    if won: wait(r'Stamina Cost', 10); return
    # Defeat -> the event dialog returns with Mark | Bypass -> always Mark (Nick) -> straight back to Explore (Kong 11-03)
    b = wait(r'^Mark', 8); tap_text(r'^Mark', boxes=b)
    say(f'  marked {title} for tribe assist')


def climb(fl, kills, need, maps, weekday):
    """Next floor by 'kills', 'map' or 'stay' (Nick 2026-11-03): F1 0 kills -> map; F2 maps kept for Thursday
    (RESERVE), earlier only a spare one; 1+ kills -> hunt the rest, never a map."""
    if kills >= need: return 'kills'
    return 'map' if maps and kills == 0 and (fl == 1 or weekday == 3 or maps - 1 >= RESERVE) else 'stay'


def best_core(b):
    """Monster Lair row to stake: highest tier, then ATK -> DEF -> HP. None if a core's tier is unknown."""
    opts = [(-int(m[1]) * TIER[m[2]], STAT[m[3]], x) for x in b
            if (m := re.match(r'(\d+)(ky|y) (ATK|DEF|HP) Beast core', x[4]))]
    return min(opts)[2] if opts and len(opts) == sum('Beast core' in x[4] for x in b) else None


def lair(b):
    opts = [x[4] for x in b if 'Beast core' in x[4]]
    x = best_core(b)
    if not x: raise Stop(f'Monster Lair: unknown core tier ({joined(b)[:250]})')
    tap_wait(x[0] + x[2] // 2, x[1] + x[3] // 2); time.sleep(1)
    r = joined(ocr())
    say(f'  lair: {opts} -> {x[4]}: {"failed" if "Failed" in r else "ok"}')


def go_up(fl):
    """Next Area -> map -> next floor's entry dialog. Kills done -> enter; else a map by Nick's strategy; else back.
    Returns (gate monster name, entered)."""
    tap_wait(924, 320)
    b = wait(r'Current Hostile', 10)
    name = [k for k, n in FLOORS.items() if n == fl + 1][0]
    p = find(b, r'^Go$|^G$') or find(b, name)
    tap_wait(*p)
    b = wait(r'Entry Requirements', 8); t = joined(b)
    k, m = re.search(r'Kill (.+?)\s*\((\d+)/(\d+)\)', t), re.search(r'Treasure Map\s*\((\d+)/', t)
    if not k: raise Stop(f'entry dialog unreadable: {t[:250]}')
    gate, kills, need, maps = k[1], int(k[2]), int(k[3]), int(m[1]) if m else 0
    gos = sorted((x for x in b if re.fullmatch(r'G[oO]', x[4])), key=lambda x: x[1])
    how = climb(fl, kills, need, maps, NOW.weekday())
    say(f'  F{fl}->F{fl + 1}: {gate} {kills}/{need}, maps {maps} -> {how}')
    if how != 'stay':
        i = 0 if how == 'kills' else 1
        if len(gos) <= i: raise Stop(f'entry dialog: {len(gos)} Go buttons')
        tap_wait(gos[i][0] + gos[i][2] // 2, gos[i][1] + gos[i][3] // 2)
        b = wait(r'Stamina Cost', 10)
        if floor(b) != fl + 1: raise Stop(f'still not on F{fl + 1}')
        return gate, True
    tap_wait(924, 360); tap_wait(96, 1812); wait(r'Stamina Cost', 10)
    return gate, False


def run(account):
    global LOG
    if not battle_on(): print('Floating Realm: no battle round now'); return
    os.makedirs(f'{R}/logs/{account}', exist_ok=True)
    LOG = f'{R}/logs/{account}/{(NOW - datetime.timedelta(hours=5)).date()}.log'
    b = ocr()
    if not find(b, r'Stamina Cost'):                       # already exploring (re-run after a stop) -> carry on
        p = find(b, r'Floating Realm', (600, 400, 1080, 900))
        if not p: raise Stop('no Floating Realm banner on the main screen')
        tap_wait(*p)
        tap_text(r'^Enter$', boxes=wait(r'^Enter$', 10))
        b = wait(r'Stamina Cost', 15)
    start = re.search(r'Points: (-?\d+)', joined(b))
    st0 = re.search(r'(\d+)/(\d+)', ' '.join(x[4] for x in b if 1150 < x[1] < 1250))
    say(f'start: F{floor(b)}, {joined(b)[joined(b).find("Points"):][:14]}, stamina {st0 and st0[0]}')
    gates, held, explores, idle, last = {}, set(), 0, 0, None
    while True:
        b = ocr(); t = joined(b)
        title = ' '.join(x[4] for x in b if 380 < x[1] + x[3] // 2 < 460)    # event dialog title
        if 'Tap anyw' in t or 'Click Anywhere' in t:
            c = find(b, r'^Confirm$'); tap_wait(*(c or (540, 500))); continue
        if 'next realm floor' in t: tap_text(r'^Cancel$', boxes=b); continue
        if 'Monster Lair' in t: lair(b); continue
        if find(b, r'^Claim$', (0, 1250, 1080, 1500)): tap_text(r'^Claim$', (0, 1250, 1080, 1500), b); continue
        fl = floor(b)
        if find(b, r'^Crush$') or find(b, r'^Attack$', (0, 1150, 1080, 1400)):
            if fl in gates and gates[fl] in title: held.discard(fl)          # gate kill -> re-check the next floor
            if find(b, r'^Crush$'): say(f'  crush {title}'); tap_text(r'^Crush$', boxes=b); time.sleep(1)
            else: fight(b, title)
            continue
        if not find(b, r'^Explore$', (0, 1250, 1080, 1500)): raise Stop(f'unknown screen: {t[:300]}')
        if fl and fl < 3 and fl not in held and find(b, r'Next Area', (760, 250, 1080, 400)):
            gates[fl], entered = go_up(fl)
            if not entered: held.add(fl)
            continue
        st, cost = re.search(r'(\d+)/(\d+)', ' '.join(x[4] for x in b if 1150 < x[1] < 1250)), re.search(r'Stamina Cost:\s*(\d+)', t)
        if not (st and cost): raise Stop(f'stamina unreadable: {t[:200]}')
        if int(st[1]) < int(cost[1]): break
        idle = idle + 1 if last == st[1] else 0; last = st[1]
        if idle >= 3: raise Stop(f'Explore ignored 3x at {st[1]} stamina (connection lost?)')
        explores += 1; tap_wait(540, 1380); time.sleep(0.5)
    end = re.search(r'Points: (-?\d+)', t)
    say(f'done: {explores} explores, F{fl}, stamina {st[1]} < cost {cost[1]}, '
        f'points {start and start[1]} -> {end and end[1]}')
    for _ in range(4):
        if near(grab().getpixel((92, 1788)), (0, 158, 230)): return
        tap_wait(96, 1812); time.sleep(1)
    raise Stop('not back on the main screen')


def logged(account):
    try: return run(account)
    except Stop as e: say(f'STOP: {e}'); raise


if __name__ == '__main__':
    main(logged, sys.argv[1])
