#!/usr/bin/env python3
# Dailies runner: the whole "Daily run order" for one account with no LLM in the loop (Nick, 2026-10-28: cost).
# usage: D=<serial> scripts/daily.py <account> [--catch-up] [step ...]   (main screen; default = all steps;
#        --catch-up = the catch-up skill's shorter list; --force = re-run steps already OK this game day
#        (state: /tmp/miniheroes-state/<account>-<game day>.done, game day starts 05:00 UTC))
# Log: every line (incl. the mission scripts' output) is appended to logs/<account>/<game day>.log.
#        OUT=<dir> sets the scratch dir (default /tmp/miniheroes-<date>/<account>) for screenshots/scripts' files.
# Each step starts and ends on the main screen. Output: one "OK|SKIP|FAIL|MANUAL <step>: ..." line per step, then
# "LEFT FOR HELPER: ..." = steps a helper must do by hand (judgment steps + failures, each with a v_*.png).
# exit 0 = ran to the end, 1 = lost the main screen (helper: recover, then re-run the steps after the last OK).
# Never spends gems except through trials.py (cap-checked) and patrol.py (cap-checked).
# UNTESTED (written 2026-10-28 from saved screenshots) — run on one account first, watch it.
import datetime, fcntl, os, re, subprocess, sys, time
from stabilize import close_x
from flow import Stop, adventure, battle, find, grab, joined, ocr, swipe, tap, tap_text, tap_wait, tickets_full, wait

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.environ['D']
near = lambda p, c, tol=40: all(abs(a - b) <= tol for a, b in zip(p, c))
NOW = datetime.datetime.now()
# game day resets 05:00 UTC (Land of Trials refresh timer, 2026-10-28). ONCE steps can't read a 'done today' counter on
# screen, so they're recorded per game day and skipped on re-runs; every other step re-checks the screen counters.
ONCE = {'hero', 'tower', 'beast', 'stage', 'sanctuary'}
GAME_DAY = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=5)).date()
MANUAL = {'pet_arena': 'Auto Deploy settings'}   # always left for a helper (rune/grocery_buy/benefit scripted 2026-10-29)


def is_main(im=None): return near((im or grab()).getpixel((92, 1788)), (0, 158, 230))


def home():
    """Back to the main screen: back arrow / popup handling, max 8 tries. Back can land on Recruit -> back again."""
    for _ in range(8):
        if is_main(): return True
        boxes = ocr()
        if tickets_full(boxes): continue
        if find(boxes, r'Do not remind me today'):
            tap_text(r'Do not remind me today', boxes=boxes)
            x = close_x(grab())                                    # back arrow can't close event popups (Dino 2026-10-28)
            if x: tap_wait(*x); time.sleep(1); continue
        if find(boxes, r'^Exit') and find(boxes, r'^Confirm$'): tap_text(r'^Confirm$', boxes=boxes); continue
        tap_wait(92, 1810); time.sleep(0.8)
    return is_main()


def red_dot(x0, y0, x1, y1, im=None):
    im = im or grab()
    return sum(1 for y in range(y0, y1, 4) for x in range(x0, x1, 4)
               if (lambda p: p[0] > 210 and p[1] < 70 and p[2] < 100)(im.getpixel((x, y)))) >= 4   # hub dots (255,0,74), Storm Rewards (230,4,74)


def script(name, *args):
    """Run another mission script; its output lines are passed through. Returns (exit code, last line)."""
    r = subprocess.run([sys.executable, os.path.join(HERE, name), *args], capture_output=True, text=True)
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    for l in lines: print('   ', l)
    if r.returncode: raise Stop(f'{name} exit {r.returncode}: {lines[-1] if lines else r.stderr[-200:]}')
    return lines[-1] if lines else ''


# ---- steps (each: main screen -> ... -> returns a short result; Stop = failed) ----

def storm_arena():
    for _ in range(4):                                   # the 2nd event card rotates; tapping it usually opens Storm
        tap_wait(880, 480); time.sleep(1.5)
        im = grab(); p = im.getpixel((400, 1580))
        # yellow Start Match + title: Treasure Vault's yellow Draw buttons passed the pixel alone (Bino 2026-10-29)
        if p[0] > 200 and p[1] > 150 and p[2] < 80 and find(ocr(), r'Start Match'): return
        home()
    raise Stop('Storm arena did not open')


def storm(cfg):
    if NOW.weekday() == 0 and NOW.hour < 17: return 'SKIP closed until Mon 17:00'
    storm_arena()
    return script('storm.py', ACCOUNT)


def ranking_rewards():
    """Arena screen: Week/Day Ranking Rewards with a gift box (red, top-right of the button) -> tap = claimed, dismiss.
    No Claim button: the tap itself claims (Cmajor Day, 2026-10-29). Nick: at the start of every Arena run."""
    got = []
    for name, x in (('week', 568), ('day', 895)):
        im = grab()
        if sum(1 for xx in range(x + 73, x + 153, 3) for yy in range(1700, 1790, 3)
               if (lambda p: p[0] > 200 and p[1] < 90 and p[2] < 110)(im.getpixel((xx, yy)))) < 15: continue
        tap_wait(x, 1828); wait(r'Tap anywhere to close|Congratulations', 6); tap_wait(540, 120); got.append(name)
    return f'ranking rewards {got}; ' if got else ''


def arena(cfg):
    tap_wait(100, 1280); wait(r'^Lineup$|Ranking', 10)   # main-screen icon is labelled "Match" in game
    return ranking_rewards() + script('arena.py', ACCOUNT)


def fishing(cfg, orders=True):
    mn = orders and re.search(r'min_order_diamonds:\s*(\d+)', cfg)
    tap_wait(624, 1780); boxes = wait(r'Order Info', 10)
    if mn:
        tap_text(r'Order Info', boxes=boxes); wait(r'Daily Order', 8)
        for row in (1, 2, 3):
            script('fish_orders.py', str(row), '6', mn.group(1))   # confirms Order Refresh popups, stops on any other
            if find(ocr(), r'Purchase'):                          # out of refresh tickets: close, buy nothing
                tap_wait(540, 1600); print('    out of refresh tickets (none bought; helper may buy per config)')
        tap_wait(973, 270)
    got = ''
    if orders and red_dot(350, 1730, 420, 1800):          # Benefit dot (fishing-pass accounts); no pass = a $ page, no dot
        tap_wait(330, 1800); c = find(wait(r'Benefit', 6), r'^Claim Reward$')
        if c: tap_wait(*c); time.sleep(1); tap_wait(540, 120); got = 'benefit claimed, '
        tap_wait(970, 238)
    boxes = ocr()
    if find(boxes, r'Auto Fishing'): return got + 'auto already running'
    for _ in range(2):                                   # Start sometimes doesn't take on the first tap (Aminor 2026-10-28)
        boxes = ocr()
        if not find(boxes, r'^Start$'): tap_wait(982, 1222); boxes = wait(r'^Start$', 8)   # settings dialog
        tap_text(r'^Start$', boxes=boxes)
        try: wait(r'Auto Fishing', 4); break
        except Stop: pass
    else: raise Stop('Auto Fishing did not start')
    return got + ('orders refreshed (no tickets bought), ' if mn else '') + 'auto started'


def patrol(cfg): return script('patrol.py', ACCOUNT)
def patrol_claim(cfg): return script('patrol.py', ACCOUNT, '--claim-only')


def shop(cfg):
    tap_wait(100, 330); boxes = wait(r'Value Pack|Free Benefits', 10)
    got = []
    c = find(boxes, r'^Claim$', (750, 700, 1040, 880))
    if c: tap_wait(*c); time.sleep(1); tap_wait(540, 120); got.append('Free Benefits')
    tap_wait(480, 1846); wait(r'Hero Pack', 8)
    if red_dot(900, 360, 1060, 440):
        tap_wait(895, 420); time.sleep(1.5); tap_wait(540, 120); tap_wait(972, 300); got.append('Select Hero 20 gems')
    return f'claimed {got or "nothing"}'


def play_pass(cfg):
    tap_wait(100, 500); wait(r'Play Pass', 10)
    got = []
    for name, x in (('weekly', 648), ('monthly', 818), ('lifetime', 988)):
        if not red_dot(x + 20, 1740, min(x + 90, 1080), 1790): continue   # dot spans y 1750-1774 (Cmajor 2026-10-29)
        tap_wait(x, 1846); time.sleep(1); boxes = ocr()
        if name == 'lifetime':
            c = find(boxes, r'^Claim Reward$')
            if c: tap_wait(*c); time.sleep(1); tap_wait(540, 120); got.append('lifetime')
        elif name == 'weekly':
            im = grab()                                  # today's Day tile has an orange header, no red dot (Cmajor 2026-10-29)
            for x2, y2, hy in ((203, 1099, 933), (540, 1099, 933), (877, 1099, 933), (203, 1486, 1320), (540, 1486, 1320),
                               (877, 1486, 1320), (540, 1700, 1704)):   # Day 7: only its header shows; tap it (untested)
                p = im.getpixel((x2 - 100, hy))
                if p[0] > 200 and 100 < p[1] < 170 and p[2] < 80:
                    tap_wait(x2, y2); time.sleep(1); tap_wait(540, 120); got.append('weekly day'); break
        else:
            for _ in range(10):                          # free-track Claim buttons; never "Continue to claim"
                c = find(ocr(), r'^Claim$', (780, 300, 960, 1750))
                if not c: break
                tap_wait(*c); time.sleep(1); tap_wait(300, 200); got.append('monthly row')
    return f'claimed {got or "nothing"}'


def tower(cfg): return script('adventure.py', ACCOUNT, 'tower')
def beast(cfg): return script('adventure.py', ACCOUNT, 'beast')


def trials(cfg):
    adventure(r'Land of Trials'); wait(r'Free attempts refresh', 10)
    return script('trials.py', ACCOUNT)


RARITY = ['Rare', 'Elite', 'Legend', 'Mythic']
PREFERRED = r'^(ATK Drill|DMG Increase Drill|Infinite Energy|Concentrated Fire|Iron Shield|Mental Fear|Battle Cry)$'


def cards(boxes, y_rarity, y_name, xs):
    """[(x, rarity index, name)] for the bonus cards whose rarity label is ~y_rarity and name ~y_name (OCR)."""
    col = lambda b: min(range(len(xs)), key=lambda i: abs(b[0] + b[2] // 2 - xs[i]))
    rar = {col(b): RARITY.index(b[4].strip()) for b in boxes if abs(b[1] - y_rarity) < 40 and b[4].strip() in RARITY}
    nam = {}                                             # names can wrap ('DMG Increase' / 'Drill', +36 px); descriptions start ~+50
    for b in sorted((b for b in boxes if -25 < b[1] - y_name < 45 and b[4].strip() not in RARITY), key=lambda b: b[1]):
        nam[col(b)] = (nam.get(col(b), '') + ' ' + b[4].strip()).strip()
    return [(xs[i], rar.get(i, -1), nam.get(i, '?')) for i in range(len(xs))]


def score(card): return (bool(re.search(PREFERRED, card[2])), card[1])   # preferred first, then rarity


def bonus_pick():
    """After a floor: 'Select Bonus Effect' (pick best) or 'Replace Bonus Effect' at 5/5 (replace only an upgrade:
    the best offer must beat the worst owned). Rules: docs/ui-routine.md Secret Sanctuary step 4-5."""
    try: boxes = wait(r'Select Bonus Effect|Replace Bonus Effect', 6)
    except Stop: return 'no bonus'
    if find(boxes, r'Select Bonus Effect'):
        best = max(cards(boxes, 716, 915, (192, 540, 884)), key=score)
        tap_wait(best[0], 950); tap_text(r'Confirm Selection', boxes=ocr()); time.sleep(1)
        return f'+{best[2]} ({RARITY[best[1]] if best[1] >= 0 else "?"})'
    if find(boxes, r'Replace Bonus'):
        # 4 owned cards visible (the 5th is off-screen right); Cmajor 2026-10-29
        offers = cards(boxes, 429, 620, (192, 540, 884)); owns = cards(boxes, 1100, 1262, (150, 460, 740, 1000))
        if any(c[1] < 0 for c in offers + owns): raise Stop(f'replace screen unreadable: {offers} / {owns}')
        offer, owned = max(offers, key=score), min(owns, key=score)
        if score(offer) > score(owned) and not re.search(PREFERRED, owned[2]):
            tap_wait(offer[0], 660); tap_wait(owned[0], 1300); tap_text(r'Replace Bonus', (500, 1600, 1060, 1750)); time.sleep(1)
            return f'{offer[2]} replaces {owned[2]}'
        tap_text(r'^Skip$', (100, 1600, 500, 1750)); time.sleep(1); return 'skip'
    return 'no bonus'


def floor_marker(im):
    """Centre of the yellow next-floor marker on the Sanctuary map, or None. It pulses (255,182..235,66..99 down to
    ~222,190,82), so colour alone also hits the flags' yellow stripes: drop yellow 60px cells with red stripes beside or
    above them (not below: the boss/demon node under the marker is red). Cmajor Ice Citadel 2026-10-29; Lava untested."""
    yel = lambda p: p[0] > 200 and 140 < p[1] < 250 and 40 < p[2] < 115 and p[0] - p[2] > 110
    red = lambda p: p[0] > 170 and p[1] < 80 and p[2] < 90
    cells = {}
    for y in range(180, 1560, 6):
        for x in range(60, 1020, 6):
            p = im.getpixel((x, y)); c = (x // 60, y // 60)
            if yel(p): cells.setdefault(c, []).append((x, y))
            elif red(p): cells.setdefault(c, []).append(None)
    reds = lambda c: sum(1 for q in cells.get(c, []) if q is None)
    ok = [(len([q for q in v if q]), c) for c, v in cells.items()
          if len([q for q in v if q]) >= 6 and not any(reds((c[0] + i, c[1] + j)) > 3 for i in (-1, 0, 1) for j in (-1, 0))]
    if not ok: return None
    c = max(ok)[1]; pts = [q for i in (-1, 0, 1) for j in (-1, 0, 1) for q in cells.get((c[0] + i, c[1] + j), []) if q]
    return sum(x for x, _ in pts) // len(pts), sum(y for _, y in pts) // len(pts)


def sanctuary_climb():
    """Map: the next floor is the node just below the yellow marker (Cmajor, Ice Citadel 2026-10-29). Crash = instant
    win; Battle -> lineup (Quick Deploy if < 5) -> Start -> Victory Confirm -> bonus pick. A loss: stop (no potions)."""
    out = []
    for _ in range(10):
        m = floor_marker(grab())
        if not m: break                                  # no marker: all floors flagged
        mx, my = m
        for dy in (90, 120):                             # node sits ~86 px below the marker centre, the floor-10 boss ~110
            tap_wait(mx, my + dy)
            try: boxes = wait(r'Floor \d+/10|Select Bonus Effect|Replace Bonus Effect', 4); break
            except Stop: pass
        else: raise Stop(f'no floor popup under the marker ({mx},{my}); done so far: {out}')
        fl = re.search(r'Floor (\d+)/10', joined(boxes))
        if find(boxes, r'Select Bonus Effect|Replace Bonus Effect'):   # far out-powered: the node tap wins outright, no popup (Cmajor floor 5)
            out.append(f'instant win {bonus_pick()}'); continue
        if find(boxes, r'^Crash$'):
            tap_text(r'^Crash$', boxes=boxes); wait(r'Tap anywhere|Congratulations', 8); tap_wait(540, 120)
            res = 'crash'
        else:
            tap_text(r'^Battle$', boxes=boxes); boxes = wait(r'^Start$', 8, (0, 1700, 1080, 1920))
            im = grab()
            ticks = sum(1 for cx in (160, 350, 540, 730, 920)
                        if sum(1 for y in range(1180, 1300, 4) for x in range(cx - 50, cx + 50, 4)
                               if (lambda p: p[1] > 190 and p[0] < 170 and p[2] < 110)(im.getpixel((x, y)))) > 15)
            if ticks < 5: tap_wait(984, 1800); time.sleep(1)
            tap_text(r'^Start$', (0, 1700, 1080, 1920), boxes)
            r = joined(wait(r'Victory|Defeat', 150))
            if 'Victory' not in r:
                tap_text(r'^Confirm$'); out.append(f'floor {fl[1]} LOST'); return 'MANUAL ' + ', '.join(out)
            tap_text(r'^Confirm$', (200, 1300, 880, 1500)); res = 'won'
        out.append(f'floor {fl[1]} {res} {bonus_pick()}')
        if fl[1] == '10': break
    return 'climbed: ' + ', '.join(out) if out else 'nothing to climb'


def sanctuary(cfg):
    adventure(r'Secret Sanctuary'); time.sleep(2); boxes = ocr()
    # map-effects intro: "Bonus Effects", or titled by the map ("Lava Cave" 2026-10-30, no "Bonus Effects") -> Confirm
    if find(boxes, r'^Confirm$', (300, 1550, 800, 1700)):
        tap_text(r'^Confirm$', (300, 1550, 800, 1700), boxes); time.sleep(1.5); boxes = ocr()
    s = find(boxes, r'^Sweep$', (300, 1700, 800, 1860))
    # the intro shows a greyed Sweep even on a fresh map; only a yellow one is real (Cmajor 2026-10-29 logged "swept"
    # on a new Ice Citadel map, nothing swept)
    if s and near(grab().getpixel((s[0] - 100, s[1])), (255, 182, 16), 40):
        tap_wait(*s); boxes = wait(r'^Confirm$', 6); tap_text(r'^Confirm$', boxes=boxes); time.sleep(2); tap_wait(540, 120)
        return 'swept'
    return sanctuary_climb()


def gate(cfg):
    adventure(r'Gate of Darkness'); boxes = wait(r'Chances left today', 10)
    left = lambda b: int(re.search(r'Chances left today\W*(\d+)', joined(b)).group(1))
    n, out = left(boxes), []
    if n >= 2:                                          # first chance: run it (time cap 3m, Nick 2026-10-29), never Restart
        tap_text(r'^Start Challenge$', (200, 880, 880, 1040), boxes)
        boxes = wait(r'^Start Challenge$', 8, (0, 1700, 1080, 1920))
        tap_text(r'^Start Challenge$', (0, 1700, 1080, 1920), boxes)
        boxes = wait(r'Start challenge from Wave|^Confirm$', 8)
        tap_text(r'^Confirm$', (560, 1080, 960, 1250), boxes)
        t0 = time.time()
        while time.time() - t0 < 180 and not find(ocr(), r'Victory|Kill Count'): time.sleep(2)
        if not find(ocr(), r'Victory|Kill Count'):     # still fighting: Pause -> Quit Battle (counts as Victory)
            tap_wait(866, 1227); b = ocr()
            if not find(b, r'Quit Battle'): tap_wait(866, 1227); b = ocr()
            tap_text(r'Quit Battle', boxes=b); wait(r'Victory|Kill Count|^Confirm$', 10)
        tap_text(r'^Confirm$', (200, 1300, 880, 1500)); boxes = wait(r'Chances left today', 10)
        n2 = left(boxes)
        if n2 != n - 1: raise Stop(f'gate chances {n} -> {n2} after a run')
        n = n2; out.append('run')
    if n >= 1:
        tap_text(r'Sweep', (850, 1000, 1060, 1110), boxes); boxes = wait(r'^Confirm$', 6)
        tap_text(r'^Confirm$', (560, 1300, 960, 1460), boxes); time.sleep(2); tap_wait(540, 120)
        n2 = left(wait(r'Chances left today', 10))
        if n2 != n - 1: raise Stop(f'gate chances {n} -> {n2} after the sweep')
        out.append('sweep')
    return f'{out or "nothing left"}'


def recruit(cfg, common_only=False):
    want = lambda k: int((re.search(rf'recruit:(?:\n\s+.*)*?\n\s+{k}:\s*(\d+)', cfg) or [0, 0])[1])
    tap_wait(96, 1810); wait(r'Recruitment|Recruit 1', 10)
    got = []
    tap_wait(188, 1610); time.sleep(1)
    for _ in range(8 if common_only else want('common')):   # catch-up: every Free chance
        boxes = ocr(); m = re.search(r'Chances\W*(\d+)', joined(boxes))
        if not m or int(m.group(1)) == 0 or not find(boxes, r'^Free$', (380, 1290, 700, 1420)): break  # ad/cooldown/done
        tap_text(r'^Free$', (380, 1290, 700, 1420), boxes)   # draw animation can outlast 2.5 s (Chien Than/xFaktor 2026-10-29)
        tap_text(r'^Confirm$', boxes=wait(r'^Confirm$', 15)); time.sleep(1); got.append('common')
    if want('ancestor') and not common_only:
        tap_wait(896, 1610); time.sleep(1); boxes = ocr()
        if find(boxes, r'^Free$', (150, 1290, 470, 1420)):
            tap_text(r'^Free$', (150, 1290, 470, 1420), boxes)
            tap_text(r'^Confirm$', boxes=wait(r'^Confirm$', 15)); got.append('ancestor')
    if want('artifact') and not common_only:
        tap_wait(618, 1840); time.sleep(1); boxes = ocr()
        p = grab().getpixel((900, 1658))
        if p[1] > 170 and p[0] < 150: got.append('ARTIFACT SKIPPED: Auto toggle is ON (helper: turn it off, draw Free)')
        elif find(boxes, r'^Free$', (380, 1580, 700, 1700)):
            tap_text(r'^Free$', (380, 1580, 700, 1700), boxes); time.sleep(2); tap_wait(540, 120); got.append('artifact')
    return f'free draws {got or "none available"}'


def hero(cfg): return script('hero.py', ACCOUNT)
def tribe(cfg): return script('tribe.py')


def num(t):
    """'239k' -> 239000, '1.2M' -> 1200000, '500' -> 500."""
    mult = {'k': 1e3, 'm': 1e6}.get(t[-1].lower(), 1)
    return int(float(t.rstrip('kKmM')) * mult)


def slash_less(t):
    """Anvil slot counter with the slash lost or read as 7/1 (Vision, 2026-10-29: 7/7 -> '77' or '777'):
    (N, M) if exactly one split gives 0 <= N <= M <= 20, else None."""
    if not t.isdigit(): return None
    c = {(int(t[:i]), int(t[j:])) for i in range(1, len(t)) for j in (i, i + 1)
         if j < len(t) and (j == i or t[i] in '71')} if len(t) <= 5 else set()
    c = {(n, m) for n, m in c if n <= m <= 20}
    return c.pop() if len(c) == 1 else None


def divine(cfg, benefit=True):
    tap_wait(798, 1780); wait(r'Arsenal', 10)
    out = []
    if benefit and red_dot(330, 1730, 420, 1800):     # Benefit (forging-pass accounts only)
        tap_wait(309, 1810); c = find(wait(r'Claim Reward', 6), r'^Claim Reward$')
        tap_wait(*c); time.sleep(1); tap_wait(540, 120); tap_wait(970, 238); out.append('benefit')
    tap_wait(980, 1810); time.sleep(2)
    out.append(script('veins.py'))
    if re.search(r'^\s*divine_forge:\s*false', cfg, re.M): return ', '.join(out + ['forge off (config)'])
    tap_wait(92, 1810); wait(r'Arsenal', 8)
    last = None
    for _ in range(14):                                 # Forge: one slot per anvil tap; crystals only, never gems
        for _ in range(4):                              # forge hammer animation hides the counters for a few s (Bino/xFaktor)
            boxes = ocr(); t = joined(boxes)
            fr = [(y, num(m.group(1)), num(m.group(2))) for x, y, w, h, b in boxes
                  for m in [re.fullmatch(r'([\d.]+[kKmM]?)/([\d.]+[kKmM]?)', b.strip())] if m]
            fr += [(y, *slash_less(b.strip())) for x, y, w, h, b in boxes if 440 < x < 600 and 1460 < y < 1520 and slash_less(b.strip())]
            slots = next((f for f in fr if f[2] <= 20), None)
            cry = next((f for f in fr if slots and 0 < f[0] - slots[0] < 160 and f[2] > 20), None)  # owned/cost under the anvil
            if slots and cry: break
            time.sleep(1.5)
        if not slots or not cry: raise Stop(f'forge counters unreadable: {t[:150]}')
        if slots[1] >= slots[2] or cry[1] < cry[2]: out.append(f'forge {slots[1]}/{slots[2]}'); break
        if slots[1] == last: out.append(f'forge did not respond at {slots[1]}/{slots[2]}'); break
        last = slots[1]; tap_wait(540, 1484); time.sleep(1.5)   # counter animates; re-read at the loop top
    return ', '.join(out)


def relic_shovels(cfg): return script('relic_shovels.py', ACCOUNT)


def stage(cfg):
    tap_wait(994, 964); boxes = wait(r'^Start$', 10, (0, 1700, 1080, 1920))
    tap_text(r'^Start$', (0, 1700, 1080, 1920), boxes)
    res = joined(wait(r'Tap anywhere to close|Victory|Defeat', 180)); tap_wait(540, 120)
    return 'Victory' if 'Victory' in res else 'Defeat' if 'Defeat' in res else 'done'


def grocery(cfg):
    tap_wait(994, 1625); time.sleep(1); tap_wait(900, 1230); wait(r'Daily Specials|Grocery', 10)
    out = script('grocery.py')
    tap_wait(966, 222)
    return out


def rune(cfg):
    """Backpack -> Rune tab -> scroll to the red (Mythic) runes -> first one without a lock -> Synthesize -> Quick
    Equip (4 lowest-tier) -> Synthesize x1. Free. Mapped on the Kong instance 2026-10-29: tiles are red runs at
    x=cx-62, lock = dark pixels at the tile's top-right; the popup (Synthesize vs 'Locked') is the final check."""
    tap_wait(994, 1625); time.sleep(1); tap_wait(900, 1775); wait(r'Backpack', 8)
    tap_wait(868, 1680); time.sleep(1); swipe(540, 1300, 540, 700, 800); time.sleep(1.2)
    im = grab(); red = lambda p: p[0] > 200 and p[1] < 120 and p[2] < 120
    tiles = []
    for cx in (160, 350, 540, 730, 920):
        s = None
        for y in range(320, 1580, 2):
            r = red(im.getpixel((cx - 62, y)))
            if r and s is None: s = y
            if not r and s is not None:
                if y - s > 120: tiles.append((s, cx))    # full tile only (partly scrolled-off ones are shorter)
                s = None
    free = [(t, cx) for t, cx in sorted(tiles)
            if not sum(1 for y in range(t - 14, t + 20) for x in range(cx + 50, cx + 80) if sum(im.getpixel((x, y))[:3]) < 150)]
    for t, cx in free[:3]:
        tap_wait(cx, t + 72)
        try: s = find(wait(r'^Synthesize$', 3, (300, 1100, 780, 1300)), r'^Synthesize$', (300, 1100, 780, 1300))
        except Stop: s = None                     # 0.8 s fixed sleep missed the popup on Dino (2026-10-30)
        if not s: tap_wait(540, 200); time.sleep(0.8); continue   # outside the popup, inside Backpack; 'Locked Runes can't be synthesized' / misread
        tap_wait(*s); tap_text(r'Quick ?Equip', (250, 1600, 580, 1720), wait(r'Quick ?Equip', 6))
        boxes = wait(r'^Synthesize$', 4, (650, 1600, 1000, 1720))
        if not find(boxes, r'^[xX]1$', (60, 1600, 200, 1720)): raise Stop('rune: multiplier is not x1')
        tap_text(r'^Synthesize$', (650, 1600, 1000, 1720), boxes)
        res = wait(r'Congratulations', 8); r = next((b[4] for b in res if 'Rune' in b[4]), 'rune')
        tap_text(r'^Confirm$', boxes=res); time.sleep(0.8); tap_wait(972, 560); time.sleep(0.8); tap_wait(972, 238)
        return f'synthesized -> {r}'
    raise Stop(f'no unlocked red rune ({len(tiles)} red tiles, {len(free)} without lock)')


SHOP_TABS = {'sanctuary': (452, False), 'tribe': (732, False), 'ruins': (980, False), 'realm': (604, True)}  # x, after tab-bar swipe


def grocery_buy(cfg):
    """Grocery shop tabs: buy each configured tile once, in the shop's own coin only (price icon colour == balance
    icon), never over the balance; popup price must match the tile. Mapped on the Kong instance 2026-10-29."""
    want = {k: [int(n) for n in re.findall(r'\d+', v)]
            for k, v in re.findall(r'^\s{4}(\w+):\s*\[([^\]]*)\]', (re.search(r'grocery_buy:.*\n((?:\s{4}.*\n?)*)', cfg) or [''] * 2)[1], re.M)}
    tap_wait(994, 1625); time.sleep(1); tap_wait(900, 1230); wait(r'Daily Specials', 10)
    out = []
    for tab in sorted(want, key=list(SHOP_TABS).index):
        x, swiped = SHOP_TABS[tab]
        if swiped: swipe(900, 546, 200, 546); time.sleep(1)
        tap_wait(x, 546); time.sleep(1); boxes = ocr()
        if not find(boxes, rf'(?i)^{tab}', (x - 160, 500, x + 160, 590)): raise Stop(f'{tab} shop tab not where expected')
        for n in want[tab]:
            im = grab(); boxes = ocr(im)
            avg = lambda x0, y0: [sum(im.getpixel((x0 + dx, y0 + dy))[i] for dx in range(-6, 7, 3) for dy in range(-6, 7, 3)) // 25 for i in range(3)]
            bal = next((num(b[4]) for b in boxes if b[0] < 300 and 350 < b[1] < 430 and re.fullmatch(r'[\d.]+[kKmM]?', b[4])), None)
            bx, by = (163, 413, 663, 913)[(n - 1) % 4], (893, 1249, 1605)[(n - 1) // 4]
            region = (bx - 125, by - 40, bx + 125, by + 40)
            if find(boxes, r'Sold', region): out.append(f'{tab} {n} sold out'); continue
            price = next((num(b[4]) for b in boxes if region[0] < b[0] + b[2] // 2 < region[2] and region[1] < b[1] + b[3] // 2 < region[3]
                          and re.fullmatch(r'[\d.]+[kKmM]?', b[4])), None)
            if bal is None or price is None: raise Stop(f'{tab} {n}: balance/price unreadable ({bal}, {price})')
            if not near(avg(bx - 73, by), avg(90, 406), 35): out.append(f'{tab} {n} SKIPPED: not priced in the shop coin'); continue
            if price > bal: out.append(f'{tab} {n} skipped: {price} > balance {bal}'); continue
            tap_wait(bx, by); boxes = wait(r'^Purchase$', 6)
            pp = next((num(b[4]) for b in boxes if 1040 < b[1] < 1140 and re.fullmatch(r'[\d.]+[kKmM]?', b[4])), None)
            if pp != price: tap_wait(540, 1850); raise Stop(f'{tab} {n}: popup price {pp} != tile price {price}')
            tap_text(r'^Purchase$', boxes=boxes); wait(r'Tap anywhere|Congratulations', 6); tap_wait(540, 1850); time.sleep(0.8)
            out.append(f'{tab} {n} bought for {price} (balance {bal})')
    tap_wait(966, 222)
    return ', '.join(out) or 'nothing configured'


def daily_mission(cfg):
    """Mapped on Kong 2026-10-28: menu icon dot ≈ (1040,1580); Mission = the ICON left of its label (the label doesn't
    react); top Claim row ≈ (860,672) claims all rows; chests above the 40/80/120/160 labels (y≈510) glow when reachable; tabs Daily (300,1686) — opens selected, no dot — and Weekly (778,1688), dot ≈ (976,1630)."""
    if not red_dot(1000, 1545, 1080, 1615): return "no red dot"
    tap_wait(994, 1625); wait(r'^Mission$', 6); time.sleep(1.2)   # side menu slides in: read the position once settled
    m = find(ocr(), r'^Mission$')
    if not m: raise Stop('Mission entry not in the side menu')
    tap_wait(m[0] - 120, m[1] - 30); wait(r'Daily Mission', 10)
    out = []
    for tab, x in (('daily', 300), ('weekly', 778)):
        if tab == 'weekly':
            time.sleep(1.5)                               # reward popup from the daily chests can still dim the tab bar
            if not red_dot(x + 120, 1595, x + 240, 1665): continue
            tap_wait(x, 1688); time.sleep(1)
        c = find(ocr(), r'^Cla[il]m$', (700, 560, 1060, 780))  # top row only — never scroll, never GO
        if c: tap_wait(*c); time.sleep(1.2); tap_wait(540, 240); out.append(f'{tab} rows')
        im = grab()                                       # reachable chests glow yellow (~350 px vs ~50 locked, Kong)
        glow = [lv for lv, cx in ((40, 423), (80, 592), (120, 762), (160, 930))
                if sum(1 for y in range(330, 470, 3) for x in range(cx - 70, cx + 70, 3)
                       if (lambda p: p[0] > 235 and p[1] > 215 and p[2] < 160)(im.getpixel((x, y)))) > 150]
        if glow:                                          # one reachable chest claims every reachable one
            cx = {40: 423, 80: 592, 120: 762, 160: 930}[glow[0]]
            tap_wait(cx, 420); time.sleep(1.2); tap_wait(540, 240); out.append(f'{tab} chests {glow}')
    tap_wait(972, 238)
    return f'{out or "nothing"}'


def fishing_rewards(cfg):
    tap_wait(624, 1780); boxes = wait(r'Order Info', 10)
    tap_text(r'Order Info', boxes=boxes); wait(r'Daily Order', 8)
    n = 0
    for y in (704, 1058, 1412):                          # "Claim" where Refresh normally is — never tap Refresh
        c = find(ocr(), r'^Cla[il]m$', (720, y - 70, 980, y + 70))
        if c: tap_wait(*c); time.sleep(1.5); tap_wait(540, 1880); n += 1
    tap_wait(973, 270)
    boxes = ocr(); stopped = find(boxes, r'Tap water surface')
    bread = next((t for x, y, w, h, t in boxes if y < 130 and x < 300 and re.fullmatch(r'\d+/\d+', t)), '?')   # top-left bread N/100
    return f'claimed {n} order rewards' + (f'; AUTO STOPPED, bread {bread} (helper: restart only if "Stop at new Archive")' if stopped else '')


# ---- claims (catch-up leftovers that used to need a helper; Nick 2026-10-28: script what's deterministic) ----
# Each one: red dot / OCR'd free button first, never a price. UNTESTED on a real claim (mapped on Tiger with
# nothing claimable) - a red dot still there afterwards -> MANUAL (helper).

def storm_rewards(cfg):
    """Storm arena Rewards (96,880): OCR the rank banner above the shield, tap only that rank's row in the panel.
    Lower rows only if the red dot survives (rank jumped since the last claim)."""
    if NOW.weekday() == 0 and NOW.hour < 17: return 'SKIP closed until Mon 17:00'
    storm_arena()
    if not red_dot(110, 830, 180, 900): return 'no red dot'
    rows = {'King': 518, 'Glory': 740, 'Gold': 962, 'Silver': 1180, 'Bronze': 1404}   # panel row y, top -> bottom
    rank = next((r for r in rows if find(ocr(), rf'^{r}', (380, 600, 700, 710))), None)
    if not rank: return 'MANUAL rank banner unreadable'

    def claim(ys):
        tap_wait(96, 880); time.sleep(1)
        for y in ys: tap_wait(372, y); time.sleep(1); tap_wait(540, 1900)   # reward popup -> dismiss
        tap_wait(972, 228); time.sleep(1)
        return red_dot(110, 830, 180, 900)

    if claim([rows[rank]]) and claim([y for y in rows.values() if y > rows[rank]]):
        return f'MANUAL red dot still on Rewards (rank {rank})'
    return f'rank rewards claimed ({rank})'


def arena_claims(cfg):
    """Arena: weekly win chests 10/20/35/50 at y≈210; reached (wins >= N) and no green check -> tap, dismiss."""
    tap_wait(100, 1280); boxes = wait(r'Winnings', 10)
    w = next((int(b[4]) for b in boxes if b[4].strip().isdigit() and b[0] < 240 and 260 < b[1] < 340), None)
    if w is None: raise Stop('win count unreadable')
    im, got = grab(), []
    for n, x in ((10, 376), (20, 536), (35, 696), (50, 864)):
        green = sum(1 for yy in range(200, 290, 3) for xx in range(x - 40, x + 40, 3)
                    if (lambda p: p[1] > 170 and p[0] < 150 and p[2] < 120)(im.getpixel((xx, yy))))
        if w >= n and green < 20:
            tap_wait(x, 210); time.sleep(1.2); tap_wait(540, 120); got.append(n)
    return f'wins {w}, chests claimed {got}' if got else f'wins {w}, nothing to claim'


def canyon_rewards(cfg):
    """Tribe -> Canyon Clash -> Rewards (88,745) red dot -> Claim Reward (repeat while it's there)."""
    if NOW.weekday() == 0 and 6 <= NOW.hour < 17: return 'SKIP closed until Mon 17:00'
    tap_wait(448, 1780); time.sleep(1.5); tap_wait(540, 1090); wait(r'Attempts', 10)
    if not red_dot(110, 690, 175, 760): return 'no red dot'
    tap_wait(88, 745); n = 0
    for _ in range(6):
        c = find(ocr(), r'^Claim Reward$')
        if not c: break
        tap_wait(*c); time.sleep(1.2); tap_wait(540, 1880); n += 1
    tap_wait(972, 240)
    return f'points rewards claimed x{n}'


def canyon(cfg):
    """Take a new EMPTY spot by the day's rule (scripts/canyon.py). No empty one -> MANUAL (helper may beat a Sentinel, never a player)."""
    if NOW.weekday() == 0 and 6 <= NOW.hour < 17: return 'SKIP closed until Mon 17:00'
    tap_wait(448, 1780); time.sleep(1.5); tap_wait(540, 1090); wait(r'Attempts', 10)
    # ponytail: one global lock - our accounts share the map and raced for the same spots (2026-10-29)
    lock = open('/tmp/miniheroes-canyon.lock', 'w'); fcntl.flock(lock, fcntl.LOCK_EX)   # freed on return
    try: return script('canyon.py', ACCOUNT)
    except Stop as e:
        if 'exit 2' in str(e): return 'MANUAL no empty platform (attack choice)'
        raise


HUB_TABS = {r'^Wish': 'wish_festival', r'^Pet': 'pet_arena', r'^Draws|^7777': '7777', r'^Match': 'match_event', r'^Weekly': 'weekly_event'}


def hub_tabs():
    """Event hub bottom tabs -> {tab: label x}. The set changes with the events, so tabs shift: find them by label
    (Kong instance 2026-10-29: 4 tabs, Wish Festival at x=480 where fixed coords said Pet Arena)."""
    tabs = {}
    for x, y, w, h, t in ocr():
        for pat, tab in HUB_TABS.items():
            if y > 1800 and re.search(pat, t) and tab not in tabs: tabs[tab] = x + w // 2
    return tabs


def claim_yellow(title):
    """Tap every exact 'Claim'/'Free' whose button is the yellow (255,182,16) - never 'Claim More', grey (locked) or
    a $/gem button - dismissing each reward; stops when none is left or the dialog `title` is gone. No reward popup
    after a tap (e.g. a no-pass account's video ad) -> Stop."""
    n = 0
    for _ in range(6):
        im = grab(); boxes = ocr(im)
        if not find(boxes, title): break
        c = next(((x + w // 2, y + h // 2) for x, y, w, h, t in boxes if t.strip() in ('Claim', 'Free')
                  and near(im.getpixel((x - 12, y + h // 2)), (255, 182, 16), 30)), None)
        if not c: break
        tap_wait(*c); wait(r'Tap anywhere|Congratulations', 4); tap_wait(540, 1880); time.sleep(0.8); n += 1
    return n


def wish_festival():
    """Sign-In (today's yellow Claim; scroll: today is often below Day 6) and Gift (Free Pack Claim, Limited 2), each
    only with its own red dot. Never Treasure Vault / Exchange / Rune Salvage (event-coin spends)."""
    got = []
    for name, icon, dot, title in (('sign-in', (880, 1520), (940, 1590, 1020, 1660), r'^Sign-In$'),
                                   ('gift', (270, 1620), (340, 1590, 420, 1660), r'^Gift$')):
        if not red_dot(*dot): continue
        tap_wait(*icon); wait(title, 6); n = 0
        for _ in range(3):                                # today's row may be below the fold
            n += claim_yellow(title)
            if name == 'gift' or n: break
            swipe(540, 1500, 540, 700, 600); time.sleep(1.2)
        if find(ocr(), title): tap_wait(966, 190); time.sleep(0.8)
        got.append(f'{name} x{n}')
    return got


def events(cfg):
    """Event hub (1st banner) bottom tabs with a red dot. Scripted: Wish Festival sign-in/gift, Weekly Event Free
    Benefits, Match Event milestones, 7777 daily Claim. Other tabs with a dot -> MANUAL. Never Again / Open All / draws / Tribe Clash (its dot never clears)."""
    tap_wait(896, 340); wait(r'Match|Weekly', 10, (0, 1760, 1080, 1920))
    out, left = [], []
    for tab, x in hub_tabs().items():
        if not red_dot(x + 30, 1720, min(x + 95, 1080), 1795): continue
        tap_wait(x, 1840); time.sleep(1.2)
        if tab == 'match_event':
            n = 0
            for sub in ((160, 320), (400, 310)):         # Canyon Warrior, Heroic Trial
                tap_wait(*sub); time.sleep(1)
                for _ in range(8):                       # top row's Claim rolls to the next milestone
                    c = find(ocr(), r'^Claim$', (740, 960, 1060, 1090))
                    if not c: break
                    tap_wait(*c); time.sleep(1.2); tap_wait(300, 200); n += 1
            out.append(f'match_event x{n}')
        elif tab == '7777':
            c = find(ocr(), r'^Claim$', (300, 1540, 780, 1680))   # never "Again"
            if c:
                tap_wait(*c)                             # 30-card result; its Confirm can take >1.5 s (Kong instance 2026-10-29)
                tap_text(r'^Confirm$', (300, 1650, 780, 1850), wait(r'^Confirm$', 15, (300, 1650, 780, 1850))); out.append('7777 daily')
        elif tab == 'wish_festival': out += wish_festival()
        elif tab == 'weekly_event':                      # 2nd sub-tab (Wish Merchant / Pet Shop / Recruit Store): Free Benefits
            tap_wait(410, 240); time.sleep(1); out.append(f'weekly free x{claim_yellow(r"Free Benefits")}')
        else: left.append(tab)
        if red_dot(x + 30, 1720, min(x + 95, 1080), 1795) and tab not in left and tab not in ('7777', 'wish_festival'):
            left.append(tab)                             # sticky dots: 7777 after its daily Claim, Wish Festival's Treasure Vault (coin draws, never)
    r = ', '.join(out) or 'nothing claimed'
    return f'MANUAL {r}; red dots left: {left}' if left else r


# catch-up (.claude/skills/catch-up): Fishing auto only, Arena, Storm, Veins + Forge (no Benefit), Patrol Claim All,
# Arena again, Tribe chat Request/Assist, Common Recruitment, Daily Mission, Fishing order rewards
CATCHUP = [('fishing_auto', lambda c: fishing(c, orders=False)), ('arena', arena), ('storm', storm),   # fishing first: Auto runs during the rest (Nick, 2026-10-29)
           ('veins_forge', lambda c: divine(c, benefit=False)), ('patrol_claim', patrol_claim), ('arena2', arena),
           ('tribe_chat', lambda c: script('tribe.py', '--chat-only')), ('common_recruit', lambda c: recruit(c, common_only=True)),
           ('storm_rewards', storm_rewards), ('arena_claims', arena_claims), ('canyon', canyon), ('canyon_rewards', canyon_rewards),
           ('events', events), ('fishing_rewards', fishing_rewards), ('daily_mission', daily_mission)]  # missions always last (Nick, 2026-10-29)
CATCHUP_MANUAL = []
# fishing first: Auto runs during the rest; patrol before arena: Speed Patrol loot refills the arena tickets, which then
# filled up mid-Trials/Stage (tickets-full popup on 5/9 accounts, 2026-10-29)
ORDER = [('fishing', fishing), ('patrol', patrol), ('storm', storm), ('arena', arena), ('shop', shop),
         ('play_pass', play_pass), ('tower', tower), ('sanctuary', sanctuary), ('gate', gate), ('beast', beast),
         ('trials', trials), ('recruit', recruit), ('hero', hero), ('tribe', tribe), ('divine', divine), ('relic_shovels', relic_shovels),
         ('stage', stage), ('patrol_claim', patrol_claim), ('rune', rune), ('arena2', arena), ('grocery', grocery), ('grocery_buy', grocery_buy),
         ('storm_rewards', storm_rewards), ('arena_claims', arena_claims), ('canyon', canyon), ('canyon_rewards', canyon_rewards),
         ('events', events), ('fishing_rewards', fishing_rewards), ('daily_mission', daily_mission)]  # missions always last (Nick, 2026-10-29)
# config key that must be present / truthy for a step to run
KEY = {'storm': None, 'arena': 'arena', 'arena2': 'arena', 'fishing': 'fishing', 'patrol': 'patrol', 'patrol_claim': 'patrol',
       'shop': 'shop_freebies', 'play_pass': 'play_pass_claims', 'tower': 'tower_of_the_throne', 'sanctuary': 'secret_sanctuary',
       'gate': 'gate_of_darkness', 'beast': 'beast_realm', 'trials': 'land_of_trials', 'recruit': 'recruit', 'hero': 'hero_upgrade',
       'tribe': 'tribe', 'divine': 'divine_weapon', 'relic_shovels': 'relic_shovels', 'stage': 'adventure_stage', 'grocery': 'grocery_free_chests',
       'daily_mission': None, 'fishing_rewards': 'fishing', 'fishing_auto': 'fishing', 'veins_forge': 'divine_weapon',
       'tribe_chat': 'tribe', 'common_recruit': 'recruit', 'storm_rewards': None, 'arena_claims': 'arena',
       'canyon_rewards': None, 'events': None, 'canyon': 'canyon_clash', 'rune': 'rune_synthesis', 'grocery_buy': 'grocery_buy'}


def enabled(cfg, key):
    if key is None: return True
    m = re.search(rf'^\s+{key}:\s*(.*)$', cfg, re.M)
    return bool(m) and m.group(1).strip().lower() not in ('false', '0', 'no')


class Tee:
    """Write to the terminal and the account log; log lines get a HH:MM:SS prefix."""
    def __init__(self, out, f): self.out, self.f, self.bol = out, f, True
    def write(self, t):
        self.out.write(t)
        for part in t.splitlines(True):
            self.f.write((f'{datetime.datetime.now():%H:%M:%S} ' if self.bol else '') + part); self.bol = part.endswith('\n')
        self.f.flush()
    def flush(self): self.out.flush()


def main(argv):
    global ACCOUNT
    catch_up = '--catch-up' in argv
    argv = [a for a in argv if a != '--catch-up']
    ACCOUNT = argv[0]; only = argv[1:]
    cfg = open(os.path.join(HERE, '..', 'accounts', ACCOUNT + '.yaml')).read()
    out = os.environ.get('OUT') or f'/tmp/miniheroes-{NOW:%F}/{ACCOUNT}'
    os.makedirs(out, exist_ok=True); os.chdir(out)
    if only: left = []                                 # single steps: report only their own leftovers
    elif catch_up: left = list(CATCHUP_MANUAL)
    else:
        left = ['pet_arena'] if NOW.weekday() < 3 and enabled(cfg, 'pet_arena') else []
    force = '--force' in argv; only = [a for a in only if a != '--force']
    state = f'/tmp/miniheroes-state/{ACCOUNT}-{GAME_DAY}.done'
    os.makedirs(os.path.dirname(state), exist_ok=True)
    lock = open(f'/tmp/miniheroes-state/{ACCOUNT}.lock', 'w')   # two runners on one account fought (Cmajor 2026-10-29)
    try: fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError: print(f'{ACCOUNT}: another daily.py is already running on it; not starting'); return 2
    done = set(open(state).read().split()) if os.path.exists(state) else set()
    log = os.path.join(HERE, '..', 'logs', ACCOUNT, f'{GAME_DAY}.log')   # permanent per-account log (git-ignored)
    os.makedirs(os.path.dirname(log), exist_ok=True)
    sys.stdout = Tee(sys.stdout, open(log, 'a'))
    print(f'=== {datetime.datetime.now():%F %H:%M:%S} daily.py {" ".join(sys.argv[1:])} (serial {D})')
    if not home(): print('FAIL start: not on the main screen'); return 1

    def step(name, fn):
        """Run one step; True = OK/SKIP/MANUAL, False = FAIL, None = lost the main screen."""
        t0, ok = time.time(), True
        try:
            r = fn(cfg)
            tag = 'MANUAL' if str(r).startswith('MANUAL') else 'SKIP' if str(r).startswith('SKIP') else 'OK'
            if tag == 'MANUAL': left.append(name)
            if tag == 'OK' and name in ONCE: open(state, 'a').write(name + '\n')
            print(f'{tag} {name} ({time.time() - t0:.0f}s): {r}', flush=True)
        except Exception as e:                           # any crash (not just Stop) fails only this step (Kong 2026-10-28)
            try: grab().resize((540, 960)).save(f'v_{name}.png')
            except Exception: pass                           # device gone (instance stopped)
            print(f'FAIL {name} ({time.time() - t0:.0f}s): {e} (screenshot {out}/v_{name}.png)', flush=True)
            ok = False
        if not home():
            print(f'FAIL home after {name}: lost the main screen; stop'); return None
        return ok

    steps = CATCHUP if catch_up else ORDER
    failed = []
    for name, fn in steps:
        if only and name not in only: continue
        if not enabled(cfg, KEY[name]): print(f'SKIP {name}: not in config', flush=True); continue
        if name in ONCE and name in done and not force: print(f'SKIP {name}: already OK this game day ({GAME_DAY})', flush=True); continue
        r = step(name, fn)
        if r is None: print('LEFT FOR HELPER:', ', '.join(left + failed + [name])); return 1
        if not r: failed.append(name)
    # one retry of each failed step: most first-pass FAILs were transient (2026-10-29: the coordinator re-ran them by
    # hand and 18 of 19 passed). Steps re-read their on-screen counters, so a retry never double-spends.
    if failed:
        print(f'--- retrying {failed}', flush=True)
        again = [n for n in failed if n != 'daily_mission'] + ['daily_mission']   # retried progress -> claim it
        for name in again:
            if name == 'daily_mission' and not enabled(cfg, KEY[name]): continue
            r = step(name, dict(steps)[name])
            if r is None: print('LEFT FOR HELPER:', ', '.join(left + failed)); return 1
            if r and name in failed: failed.remove(name)
    left += failed
    print('LEFT FOR HELPER:', ', '.join(f'{k} ({MANUAL[k]})' if k in MANUAL else k for k in left))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
