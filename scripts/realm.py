#!/usr/bin/env python3
# Floating Realm (Tribe cross-server event, every 2 weeks; battle Tue/Wed/Thu 10:00-22:00 UTC): spend all stamina
# exploring. Rules: docs/ui-routine.md "Floating Realm" (Nick, 2026-11-03).
# usage: D=<serial> scripts/realm.py <account> [--max-floor N]   (main or explore screen; ends on the main screen)
#        --max-floor 2 = never climb to F3 (Nick asks per account)
# End: claim the reached Target (stamina-used) milestones. Treasure -> Claim, weak monster -> Crush, monster/player -> Attack whatever the CP, Defeat -> Mark (Nick), Monster Lair -> stake
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


def skip_on(im):
    """Explore screen's Skip checkbox (816,1532) ticked = green check (Nick, 2026-11-03: tick it before exploring)."""
    import numpy as np
    r, g, b = np.asarray(im.crop((790, 1505, 845, 1560)).convert('RGB'), dtype=int).transpose(2, 0, 1)
    return ((g > 150) & (g > r + 40) & (g > b + 40)).sum() > 50


def floor(b):
    t = ' '.join(x[4] for x in b if x[0] > 760 and x[1] < 300)    # top-right floor card label
    return next((n for k, n in FLOORS.items() if k in t), None)


def fight(b, title):
    """Monster/player dialog with Attack: always attack, CP doesn't matter; a Defeat is Marked (Nick, 2026-11-03)."""
    foe = cps(b, 540, 640)
    tap_text(r'^Attack$', (0, 1150, 1080, 1400), b)
    try: b = wait(r'^Start$', 10)
    except Stop:   # Attack tap ignored, dialog still up (Tiger 2026-11-03) -> one more try
        tap_text(r'^Attack$', (0, 1150, 1080, 1400)); b = wait(r'^Start$', 10)
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
    # held maps: the scroll counter top left of the map; the dialog's "(m/1)" may be capped at the 1 needed
    held = [int(x[4]) for x in b if x[0] < 300 and x[1] < 120 and x[4].isdigit()]
    name = [k for k, n in FLOORS.items() if n == fl + 1][0]
    p = find(b, r'^Go$|^G$') or find(b, name)
    tap_wait(*p)
    b = wait(r'Entry Requirements', 8); t = joined(b)
    k, m = re.search(r'Kill (.+?)\s*\((\d+)/(\d+)\)', t), re.search(r'Treasure Map\s*\((\d+)/', t)
    if not k: raise Stop(f'entry dialog unreadable: {t[:250]}')
    gate, kills, need, maps = k[1], int(k[2]), int(k[3]), held[0] if held else int(m[1]) if m else 0
    gos = sorted((x for x in b if re.fullmatch(r'G[oO]', x[4])), key=lambda x: x[1])
    how = climb(fl, kills, need, maps, NOW.weekday())
    say(f'  F{fl}->F{fl + 1}: {gate} {kills}/{need}, maps {maps} (counter {held}, dialog {m and m[1]}) -> {how}')
    if how != 'stay':
        i = 0 if how == 'kills' else 1
        if len(gos) <= i: raise Stop(f'entry dialog: {len(gos)} Go buttons')
        tap_wait(gos[i][0] + gos[i][2] // 2, gos[i][1] + gos[i][3] // 2)
        wait(r'Stamina Cost', 10)
        wait(name, 8, (760, 0, 1080, 300))   # floor card label updates a beat later (Aminor 2026-11-03: false "still not on F2")
        return gate, True
    tap_wait(924, 360); tap_wait(96, 1812); wait(r'Stamina Cost', 10)
    return gate, False


def targets():
    """Event screen -> Target (976,1320) -> Claim each reached stamina milestone (Nick 2026-11-03: collect rewards at the
    end). A claimed row drops to the bottom, so reached ones sit on top. Congratulations popup closes on its 'Tap
    anywhere to close' text (540,1208); the dialog's title shows through the popup, so wait for that text to go."""
    tap_wait(976, 1320); b = wait(r'Target Rewards', 8)
    got = []
    while (c := find(b, r'^Claim$', (700, 200, 1080, 1750))) and len(got) < 20:
        got.append(re.search(r'Realm: (\d+)', ' '.join(x[4] for x in b if c[1] - 200 < x[1] < c[1] - 60)))
        tap_wait(*c); wait(r'Tap anywhere', 5); tap_wait(540, 1208)
        for _ in range(8):
            b = ocr()
            if not find(b, r'Tap anywhere'): break
            time.sleep(0.7)
        else: raise Stop('Target reward popup did not close')
    say(f'targets claimed: {[m and int(m[1]) for m in got] or "none"}')
    tap_wait(972, 228); wait(r'^Enter$', 8)


def run(account, max_floor=3):
    global LOG
    if not battle_on(): print('Floating Realm: no battle round now'); return
    os.makedirs(f'{R}/logs/{account}', exist_ok=True)
    LOG = f'{R}/logs/{account}/{(NOW - datetime.timedelta(hours=5)).date()}.log'
    b = ocr()
    if not find(b, r'Stamina Cost'):                       # already exploring (re-run after a stop) -> carry on
        if not find(b, r'^Enter$'):                        # not on the event screen yet -> main screen banner
            p = find(b, r'Floating Realm', (600, 400, 1080, 900))
            if not p: raise Stop('no Floating Realm banner on the main screen')
            tap_wait(*p); b = wait(r'^Enter$', 10)
        tap_text(r'^Enter$', boxes=b)
        b = wait(r'Stamina Cost', 15)
    start = re.search(r'Points: (-?\d+)', joined(b))
    st0 = re.search(r'(\d+)/(\d+)', ' '.join(x[4] for x in b if 1150 < x[1] < 1250))
    say(f'start: F{floor(b)}, {joined(b)[joined(b).find("Points"):][:14]}, stamina {st0 and st0[0]}')
    gates, held, explores, idle, last, skips, knocks = {}, set(), 0, 0, None, 0, 0
    while True:
        im = grab(); b = ocr(im); t = joined(b)
        title = ' '.join(x[4] for x in b if 380 < x[1] + x[3] // 2 < 460)    # event dialog title
        if 'Tap anyw' in t or 'Click Anywhere' in t:
            c = find(b, r'^Confirm$'); tap_wait(*(c or (540, 500))); continue
        if 'next realm floor' in t: tap_text(r'^Cancel$', boxes=b); continue
        if 'You were defeated by' in t:      # a player beat us: lost a core, back a floor; Confirm only (Chien Than 11-03)
            knocks += 1
            if knocks > 2: raise Stop('knock-back dialog: Confirm ignored 2x (connection lost?)')
            if knocks == 1: say(f'  {t[t.find("You were defeated"):][:110]}')
            tap_text(r'^Confirm$', boxes=b); time.sleep(1); continue
        knocks = 0
        if 'Monster Lair' in t: lair(b); continue
        if find(b, r'^Claim$', (0, 1250, 1080, 1500)): tap_text(r'^Claim$', (0, 1250, 1080, 1500), b); continue
        fl = floor(b)
        if find(b, r'^Crush$') or find(b, r'^Attack$', (0, 1150, 1080, 1400)):
            if fl in gates and gates[fl] in title: held.discard(fl)          # gate kill -> re-check the next floor
            if find(b, r'^Crush$'): say(f'  crush {title}'); tap_text(r'^Crush$', boxes=b); time.sleep(1)
            else: fight(b, title)
            continue
        if not find(b, r'^Explore$', (0, 1250, 1080, 1500)): raise Stop(f'unknown screen: {t[:300]}')
        if fl and fl < max_floor and fl not in held and find(b, r'Next Area', (760, 250, 1080, 400)):
            gates[fl], entered = go_up(fl)
            if not entered: held.add(fl)
            continue
        st, cost = re.search(r'(\d+)/(\d+)', ' '.join(x[4] for x in b if 1150 < x[1] < 1250)), re.search(r'Stamina Cost:\s*(\d+)', t)
        if not (st and cost): raise Stop(f'stamina unreadable: {t[:200]}')
        if int(st[1]) < int(cost[1]): break
        idle = idle + 1 if last == st[1] else 0; last = st[1]
        if idle >= 3: raise Stop(f'Explore ignored 3x at {st[1]} stamina (connection lost?)')
        if find(b, r'^Skip$', (700, 1450, 1080, 1600)) and not skip_on(im):
            skips += 1
            if skips > 2: raise Stop('Skip checkbox did not tick after 2 taps')
            say('  tick Skip'); tap_wait(816, 1532); continue
        explores += 1; tap_wait(540, 1380); time.sleep(0.5)
    end = re.search(r'Points: (-?\d+)', t)
    say(f'done: {explores} explores, F{fl}, stamina {st[1]} < cost {cost[1]}, '
        f'points {start and start[1]} -> {end and end[1]}')
    tap_wait(96, 1812); wait(r'^Enter$', 8)                # explore -> event screen
    targets()
    for _ in range(4):
        if near(grab().getpixel((92, 1788)), (0, 158, 230)): return
        tap_wait(96, 1812); time.sleep(1)
    raise Stop('not back on the main screen')


def logged(account, max_floor):
    try: return run(account, max_floor)
    except Stop as e: say(f'STOP: {e}'); raise


if __name__ == '__main__':
    main(logged, sys.argv[1], int(sys.argv[sys.argv.index('--max-floor') + 1]) if '--max-floor' in sys.argv else 3)
