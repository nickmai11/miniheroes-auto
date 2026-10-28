#!/usr/bin/env python3
# Dailies runner: the whole "Daily run order" for one account with no LLM in the loop (Nick, 2026-10-28: cost).
# usage: D=<serial> scripts/daily.py <account> [step ...]      (game on the main screen; default = all steps)
#        OUT=<dir> sets the scratch dir (default /tmp/miniheroes-<date>/<account>) for screenshots/scripts' files.
# Each step starts and ends on the main screen. Output: one "OK|SKIP|FAIL|MANUAL <step>: ..." line per step, then
# "LEFT FOR HELPER: ..." = steps a helper must do by hand (judgment steps + failures, each with a v_*.png).
# exit 0 = ran to the end, 1 = lost the main screen (helper: recover, then re-run the steps after the last OK).
# English UI only. Never spends gems except through trials.py (cap-checked) and patrol.py (cap-checked).
# UNTESTED (written 2026-10-28 from saved screenshots) — run on one account first, watch it.
import datetime, os, re, subprocess, sys, time
from flow import Stop, adventure, battle, find, grab, joined, ocr, swipe, tap, tap_text, tap_wait, wait

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.environ['D']
near = lambda p, c, tol=40: all(abs(a - b) <= tol for a, b in zip(p, c))
NOW = datetime.datetime.now()
MANUAL = {'pet_arena': 'Auto Deploy settings', 'storm_rewards': 'rank-row icons', 'match_claims': 'chest/gift layout',
          'canyon': 'spot choice', 'sanctuary_climb': 'bonus-card choice', 'rune': 'locked-rune grid',
          'grocery_buy': 'tile price vs balance', 'events': 'red-dot judgment', 'fishing_benefit': 'not mapped for OCR'}


def is_main(im=None): return near((im or grab()).getpixel((92, 1788)), (0, 158, 230))


def home():
    """Back to the main screen: back arrow / popup handling, max 8 tries. Back can land on Recruit -> back again."""
    for _ in range(8):
        if is_main(): return True
        boxes = ocr()
        if find(boxes, r'Do not remind me today'): tap_text(r'Do not remind me today', boxes=boxes)
        if find(boxes, r'^Exit') and find(boxes, r'^Confirm$'): tap_text(r'^Confirm$', boxes=boxes); continue
        tap_wait(92, 1810); time.sleep(0.8)
    return is_main()


def red_dot(x0, y0, x1, y1, im=None):
    im = im or grab()
    return sum(1 for y in range(y0, y1, 4) for x in range(x0, x1, 4)
               if (lambda p: p[0] > 210 and p[1] < 70 and p[2] < 70)(im.getpixel((x, y)))) >= 4


def script(name, *args):
    """Run another mission script; its output lines are passed through. Returns (exit code, last line)."""
    r = subprocess.run([sys.executable, os.path.join(HERE, name), *args], capture_output=True, text=True)
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    for l in lines: print('   ', l)
    if r.returncode: raise Stop(f'{name} exit {r.returncode}: {lines[-1] if lines else r.stderr[-200:]}')
    return lines[-1] if lines else ''


# ---- steps (each: main screen -> ... -> returns a short result; Stop = failed) ----

def storm(cfg):
    if NOW.weekday() == 0 and NOW.hour < 17: return 'SKIP closed until Mon 17:00'
    for _ in range(4):                                   # the 2nd event card rotates; tapping it usually opens Storm
        tap_wait(880, 480); time.sleep(1.5)
        im = grab(); p = im.getpixel((400, 1580))
        if p[0] > 200 and p[1] > 150 and p[2] < 80: break  # yellow Start Match = Storm arena
        home()
    else: raise Stop('Storm arena did not open')
    return script('storm.py')


def match(cfg):
    tap_wait(100, 1280); wait(r'^Lineup$|Ranking', 10)
    return script('match.py', ACCOUNT)


def fishing(cfg):
    mn = re.search(r'min_order_diamonds:\s*(\d+)', cfg)
    tap_wait(624, 1780); boxes = wait(r'Order Info', 10)
    if mn:
        tap_text(r'Order Info', boxes=boxes); wait(r'Daily Order', 8)
        for row in (1, 2, 3):
            for _ in range(2):
                script('fish_orders.py', str(row), '6', mn.group(1))   # stops (no tap) on any popup
                boxes = ocr()
                if find(boxes, r'Do not remind me today'):           # first refresh of the day: tick alone, then Confirm
                    tap_text(r'Do not remind me today', boxes=boxes); time.sleep(1); tap_wait(757, 1211); continue
                if find(boxes, r'Purchase'):                          # out of refresh tickets: close, buy nothing
                    tap_wait(540, 1600); print('    out of refresh tickets (none bought; helper may buy per config)')
                break
        tap_wait(973, 270)
    boxes = ocr()
    if find(boxes, r'Auto Fishing'): return 'auto already running'
    tap_wait(982, 1222); boxes = wait(r'^Start$', 8)
    tap_text(r'^Start$', boxes=boxes); time.sleep(1.5)
    if not find(ocr(), r'Auto Fishing'): raise Stop('Auto Fishing did not start')
    return 'orders refreshed (no tickets bought), auto started'


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
        if not red_dot(x + 20, 1770, x + 90, 1830): continue
        tap_wait(x, 1846); time.sleep(1); boxes = ocr()
        if name == 'lifetime':
            c = find(boxes, r'^Claim Reward$')
            if c: tap_wait(*c); time.sleep(1); tap_wait(540, 120); got.append('lifetime')
        elif name == 'weekly':
            for x2, y2 in ((203, 1099), (540, 1099), (877, 1099), (203, 1486), (540, 1486), (877, 1486), (540, 1700)):
                if red_dot(x2 + 40, y2 - 160, x2 + 160, y2 - 60):
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


def sanctuary(cfg):
    adventure(r'Secret Sanctuary'); time.sleep(2); boxes = ocr()
    if find(boxes, r'Bonus Effects') and find(boxes, r'^Confirm$', (300, 1550, 800, 1700)):
        tap_text(r'^Confirm$', (300, 1550, 800, 1700), boxes); boxes = ocr()
    s = find(boxes, r'^Sweep$', (300, 1700, 800, 1860))
    if not s: return 'MANUAL no Sweep offered -> climb (sanctuary_climb)'
    tap_wait(*s); boxes = wait(r'^Confirm$', 6); tap_text(r'^Confirm$', boxes=boxes); time.sleep(2); tap_wait(540, 120)
    return 'swept'


def gate(cfg):
    adventure(r'Gate of Darkness'); boxes = wait(r'Chances left today', 10)
    left = lambda b: int(re.search(r'Chances left today\W*(\d+)', joined(b)).group(1))
    n, out = left(boxes), []
    if n >= 2:                                          # first chance: run it (time cap 1m30s), never Restart
        tap_text(r'^Start Challenge$', (200, 880, 880, 1040), boxes)
        boxes = wait(r'^Start Challenge$', 8, (0, 1700, 1080, 1920))
        tap_text(r'^Start Challenge$', (0, 1700, 1080, 1920), boxes)
        boxes = wait(r'Start challenge from Wave|^Confirm$', 8)
        tap_text(r'^Confirm$', (560, 1080, 960, 1250), boxes)
        t0 = time.time()
        while time.time() - t0 < 90 and not find(ocr(), r'Victory|Kill Count'): time.sleep(2)
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


def recruit(cfg):
    want = lambda k: int((re.search(rf'recruit:(?:\n\s+.*)*?\n\s+{k}:\s*(\d+)', cfg) or [0, 0])[1])
    tap_wait(96, 1810); wait(r'Recruitment|Recruit 1', 10)
    got = []
    tap_wait(188, 1610); time.sleep(1)
    for _ in range(want('common')):
        boxes = ocr(); m = re.search(r'Chances\W*(\d+)', joined(boxes))
        if not m or int(m.group(1)) == 0 or not find(boxes, r'^Free$', (380, 1290, 700, 1420)): break  # ad/cooldown/done
        tap_text(r'^Free$', (380, 1290, 700, 1420), boxes); time.sleep(2.5)
        c = find(ocr(), r'^Confirm$'); tap_wait(*(c or (540, 1700))); time.sleep(1); got.append('common')
    if want('ancestor'):
        tap_wait(896, 1610); time.sleep(1); boxes = ocr()
        if find(boxes, r'^Free$', (150, 1290, 470, 1420)):
            tap_text(r'^Free$', (150, 1290, 470, 1420), boxes); time.sleep(2.5)
            c = find(ocr(), r'^Confirm$'); tap_wait(*(c or (300, 1755))); got.append('ancestor')
    if want('artifact'):
        tap_wait(618, 1840); time.sleep(1); boxes = ocr()
        p = grab().getpixel((900, 1658))
        if p[1] > 170 and p[0] < 150: got.append('ARTIFACT SKIPPED: Auto toggle is ON (helper: turn it off, draw Free)')
        elif find(boxes, r'^Free$', (380, 1580, 700, 1700)):
            tap_text(r'^Free$', (380, 1580, 700, 1700), boxes); time.sleep(2); tap_wait(540, 120); got.append('artifact')
    return f'free draws {got or "none available"}'


def hero(cfg): return script('hero.py', ACCOUNT)
def tribe(cfg): return script('tribe.py')


def divine(cfg):
    tap_wait(798, 1780); wait(r'Arsenal', 10)
    out = []
    if red_dot(330, 1730, 420, 1800):                 # Benefit (forging-pass accounts only)
        tap_wait(309, 1810); c = find(wait(r'Claim Reward', 6), r'^Claim Reward$')
        tap_wait(*c); time.sleep(1); tap_wait(540, 120); tap_wait(970, 238); out.append('benefit')
    tap_wait(980, 1810); time.sleep(2)
    out.append(script('veins.py'))
    tap_wait(92, 1810); wait(r'Arsenal', 8)
    for _ in range(14):                                 # Forge: one slot per anvil tap; crystals only, never gems
        boxes = ocr(); t = joined(boxes)
        if re.search(r'\d\d:\d\d:\d\d', t): out.append('forge running (timer); skipped'); break
        fr = [(y, *map(int, b.split('/'))) for x, y, w, h, b in boxes if re.fullmatch(r'\d+/\d+', b.strip())]
        slots = next((f for f in fr if f[2] <= 20), None)
        cry = next((f for f in fr if slots and 0 < f[0] - slots[0] < 160 and f[2] > 20), None)  # owned/cost under the anvil
        if not slots or not cry: raise Stop(f'forge counters unreadable: {t[:150]}')
        if slots[1] >= slots[2] or cry[1] < cry[2]: out.append(f'forge {slots[1]}/{slots[2]}'); break
        tap_wait(540, 1484); time.sleep(1)
        n2 = next((int(b.split('/')[0]) for x, y, w, h, b in ocr() if re.fullmatch(r'\d+/\d{1,2}', b.strip())), slots[1])
        if n2 <= slots[1]: out.append('forge did not respond'); break
    return ', '.join(out)


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


def daily_mission(cfg):
    if not red_dot(1010, 1580, 1070, 1640): return 'no red dot'
    tap_wait(994, 1625); time.sleep(1)
    m = find(ocr(), r'^Mission$')
    if not m: raise Stop('Mission entry not in the side menu')
    tap_wait(*m); wait(r'Daily Mission|Activity', 10)
    out = []
    for tab, x in (('daily', 297), ('weekly', 779)):
        if not red_dot(x + 60, 1640, x + 200, 1690): continue
        tap_wait(x, 1693); time.sleep(1)
        c = find(ocr(), r'^Cla[il]m$', (700, 380, 1060, 900))  # top row only — never scroll, never GO
        if c: tap_wait(*c); time.sleep(1); tap_wait(540, 120); out.append(f'{tab} rows')
        boxes = ocr()
        pts = [(x0 + w // 2, y0, int(t)) for x0, y0, w, h, t in boxes if t.strip().isdigit() and y0 < 380 and int(t) % 10 == 0]
        for cx, cy, _ in sorted(pts, key=lambda p: p[2]):  # lowest chest first; one reachable tap claims all reachable
            if red_dot(cx - 20, cy - 120, cx + 60, cy - 20):
                tap_wait(cx, cy - 60); time.sleep(1); tap_wait(540, 120); out.append(f'{tab} chests'); break
    tap_wait(972, 238)
    return f'claimed {out or "nothing"}'


def fishing_rewards(cfg):
    tap_wait(624, 1780); boxes = wait(r'Order Info', 10)
    tap_text(r'Order Info', boxes=boxes); wait(r'Daily Order', 8)
    n = 0
    for y in (704, 1058, 1412):                          # "Claim" where Refresh normally is — never tap Refresh
        c = find(ocr(), r'^Cla[il]m$', (720, y - 70, 980, y + 70))
        if c: tap_wait(*c); time.sleep(1.5); tap_wait(540, 1880); n += 1
    tap_wait(973, 270)
    stopped = find(ocr(), r'Tap water surface')
    return f'claimed {n} order rewards' + ('; AUTO STOPPED (helper: restart only if "Stop at new Archive")' if stopped else '')


ORDER = [('storm', storm), ('match', match), ('fishing', fishing), ('patrol', patrol), ('shop', shop),
         ('play_pass', play_pass), ('tower', tower), ('sanctuary', sanctuary), ('gate', gate), ('beast', beast),
         ('trials', trials), ('recruit', recruit), ('hero', hero), ('tribe', tribe), ('divine', divine),
         ('stage', stage), ('patrol_claim', patrol_claim), ('match2', match), ('grocery', grocery),
         ('daily_mission', daily_mission), ('fishing_rewards', fishing_rewards)]
# config key that must be present / truthy for a step to run
KEY = {'storm': None, 'match': 'match', 'match2': 'match', 'fishing': 'fishing', 'patrol': 'patrol', 'patrol_claim': 'patrol',
       'shop': 'shop_freebies', 'play_pass': 'play_pass_claims', 'tower': 'tower_of_the_throne', 'sanctuary': 'secret_sanctuary',
       'gate': 'gate_of_darkness', 'beast': 'beast_realm', 'trials': 'land_of_trials', 'recruit': 'recruit', 'hero': 'hero_upgrade',
       'tribe': 'tribe', 'divine': 'divine_weapon', 'stage': 'adventure_stage', 'grocery': 'grocery_free_chests',
       'daily_mission': None, 'fishing_rewards': 'fishing'}


def enabled(cfg, key):
    if key is None: return True
    m = re.search(rf'^\s+{key}:\s*(.*)$', cfg, re.M)
    return bool(m) and m.group(1).strip().lower() not in ('false', '0', 'no')


def main(argv):
    global ACCOUNT
    ACCOUNT = argv[0]; only = argv[1:]
    cfg = open(os.path.join(HERE, '..', 'accounts', ACCOUNT + '.yaml')).read()
    out = os.environ.get('OUT') or f'/tmp/miniheroes-{NOW:%F}/{ACCOUNT}'
    os.makedirs(out, exist_ok=True); os.chdir(out)
    left = [k for k in MANUAL if k not in ('pet_arena',) or (NOW.weekday() < 3 and enabled(cfg, 'pet_arena'))]
    left = [k for k in left if k != 'grocery_buy' or 'grocery_buy' in cfg]
    if not home(): print('FAIL start: not on the main screen'); return 1
    for name, fn in ORDER:
        if only and name not in only: continue
        if not enabled(cfg, KEY[name]): print(f'SKIP {name}: not in config', flush=True); continue
        t0 = time.time()
        try:
            r = fn(cfg)
            tag = 'MANUAL' if str(r).startswith('MANUAL') else 'SKIP' if str(r).startswith('SKIP') else 'OK'
            if tag == 'MANUAL': left.append(name)
            print(f'{tag} {name} ({time.time() - t0:.0f}s): {r}', flush=True)
        except Stop as e:
            grab().resize((540, 960)).save(f'v_{name}.png')
            print(f'FAIL {name} ({time.time() - t0:.0f}s): {e} (screenshot {out}/v_{name}.png)', flush=True)
            left.append(name)
        if not home():
            print(f'FAIL home after {name}: lost the main screen; stop'); print('LEFT FOR HELPER:', ', '.join(left)); return 1
    print('LEFT FOR HELPER:', ', '.join(f'{k} ({MANUAL[k]})' if k in MANUAL else k for k in left))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
