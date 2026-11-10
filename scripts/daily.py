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
from tap import diff, thumb
from flow import Stop, adventure, battle, find, grab, joined, lone_hero, ocr, swipe, tap, tap_text, tap_wait, tickets_full, wait, watch_ad

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.environ['D']
near = lambda p, c, tol=40: all(abs(a - b) <= tol for a, b in zip(p, c))
NOW = datetime.datetime.now()
# game day resets 05:00 UTC (Land of Trials refresh timer, 2026-10-28). ONCE steps can't read a 'done today' counter on
# screen, so they're recorded per game day and skipped on re-runs; every other step re-checks the screen counters.
ONCE = {'hero', 'tower', 'beast', 'stage', 'sanctuary', 'pet_arena'}
GAME_DAY = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=5)).date()


def is_main(im=None): return near((im or grab()).getpixel((92, 1788)), (0, 158, 230))


def home():
    """Back to the main screen: back arrow / popup handling, max 8 tries. Back can land on Recruit -> back again."""
    for _ in range(8):
        if is_main(): return True
        boxes = ocr()
        try:
            if tickets_full(boxes): continue
        except Stop as e: print(f'    {e}', flush=True); return False
        if find(boxes, r'Do not remind me today'):
            tap_text(r'Do not remind me today', boxes=boxes)
            x = close_x(grab())                                    # back arrow can't close event popups (Dino 2026-10-28)
            if x: tap_wait(*x); time.sleep(1); continue
        if find(boxes, r'^Exit') and find(boxes, r'^Confirm$'): tap_text(r'^Confirm$', boxes=boxes); continue
        if find(boxes, r'Network issue') and find(boxes, r'^Confirm$'):   # mid-battle (xFaktor gate 2026-11-10): Confirm reloads
            tap_text(r'^Confirm$', boxes=boxes); print('    network issue popup -> Confirm (game reloads)', flush=True)
            for _ in range(60):
                if is_main(): break
                time.sleep(1)
            continue
        tap_wait(92, 1810); time.sleep(0.8)
    for _ in range(3):                                   # screens without the back arrow (hero detail, Cmajor 2026-10-31):
        if is_main(): return True                        # Android Back - never on main (it opens a dialog there)
        subprocess.run(['adb', '-s', D, 'shell', 'input', 'keyevent', '4']); time.sleep(1.2)
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

def storm_closed():
    """Main screen: Storm card says 'Coming Soon' = season over (Sun 06:00, 2026-11-01: 4 blind card taps x retry on
    every account before this)."""
    boxes = ocr()
    return bool(find(boxes, r'Storm Battlefield') and find(boxes, r'Coming Soon'))


def storm_welcome(boxes):
    """New season (Mon 17:00): Storm opens on 'Welcome to Storm Battlefield! Please deploy your Heroes' instead of the
    arena (every account failed 'arena did not open', 2026-11-02). Deploy -> Quick Deploy -> Save -> back -> Start."""
    boxes = wait(r'^(Deploy|Start)$', 6, (300, 1150, 780, 1300))   # the title shows before the button (Cmajor 2026-11-02)
    if find(boxes, r'^Deploy$', (300, 1150, 780, 1300)):
        tap_text(r'^Deploy$', (300, 1150, 780, 1300), boxes); wait(r'Quick Deploy', 6)
        tap_wait(984, 1800); wait(r'[1-9]\d*K', 5, (300, 150, 780, 240))
        tap_wait(540, 1808); time.sleep(0.8); tap_wait(88, 1812)
        boxes = wait(r'^Start$', 6, (300, 1150, 780, 1300))
    tap_text(r'^Start$', (300, 1150, 780, 1300), boxes); wait(r'Start Match', 8)
    print('    storm: new-season welcome -> team deployed (Quick Deploy), Start', flush=True)


def storm_arena():
    for _ in range(6):                                   # the 2nd event card rotates: a tap opens Storm only while it shows
        if storm_closed(): raise Stop('SKIP_CLOSED')
        tap(880, 480); t0 = time.time()
        while time.time() - t0 < 3:
            boxes = ocr()
            if find(boxes, r'Welcome to Storm'): storm_welcome(boxes); boxes = ocr()
            p = grab().getpixel((400, 1580))
            # yellow Start Match + title: Treasure Vault's yellow Draw buttons passed the pixel alone (Bino 2026-10-29)
            if p[0] > 200 and p[1] > 150 and p[2] < 80 and find(boxes, r'Start Match'): return
            time.sleep(0.4)
        home()
    raise Stop('Storm arena did not open')


def storm_block(cfg):
    """Server block s201-210, s211-220, ...: our accounts in one block can be matched against each other in Storm."""
    srv = int((re.search(r'^\s+server:\s*(\d+)', cfg, re.M) or [0, 0])[1])
    return f's{(srv - 1) // 10 * 10 + 1}'


def storm(cfg):
    if NOW.weekday() == 0 and NOW.hour < 17: return 'SKIP closed until Mon 17:00'
    # one Storm at a time per server block - parallel runners wait here (Nick 2026-11-02: they'd attack each other)
    with open(f'/tmp/miniheroes-state/storm-{storm_block(cfg)}.lock', 'w') as lock:
        t0 = time.time(); fcntl.flock(lock, fcntl.LOCK_EX)
        if time.time() - t0 > 2: print(f'    storm: waited {time.time() - t0:.0f}s for {storm_block(cfg)}', flush=True)
        try: storm_arena()
        except Stop as e:
            if 'SKIP_CLOSED' in str(e): return 'SKIP season closed (Storm card: Coming Soon)'
            raise
        out = script('storm.py', ACCOUNT)
        rew = storm_rewards()                            # same visit: Rewards is part of Storm (Nick, 2026-10-31)
    return ('MANUAL ' if rew.startswith('MANUAL') else '') + f'{out}; rewards: {rew}'


def ranking_rewards():
    """Arena screen: Week/Day Ranking Rewards with a gift box (red, top-right of the button) -> tap = claimed, dismiss.
    No Claim button: the tap itself claims (Cmajor Day, 2026-10-29). Nick: at the start of every Arena run."""
    got = []
    for name, x in (('week', 568), ('day', 895)):
        im = grab()
        if sum(1 for xx in range(x + 73, x + 153, 3) for yy in range(1700, 1790, 3)
               if (lambda p: p[0] > 200 and p[1] < 90 and p[2] < 110)(im.getpixel((xx, yy)))) < 15: continue
        tap_wait(x, 1828); wait(r'Tap anywhere to close|Congratulation', 6); tap_wait(540, 120); got.append(name)
    return f'ranking rewards {got}; ' if got else ''


def arena(cfg):
    tap_wait(100, 1280); wait(r'^Lineup$|Ranking', 10)   # main-screen icon is labelled "Match" in game
    out = ranking_rewards() + script('arena.py', ACCOUNT)
    return f'{out}; {arena_claims()}'                   # same visit: win chests are part of Arena (Nick, 2026-10-31)


def scrolls():
    """Order Refresh Scroll count, top-left of the Daily Order dialog (left of its '+')."""
    return next((int(t) for x, y, w, h, t in ocr() if 120 < x + w // 2 < 250 and 390 < y + h // 2 < 460 and t.strip().isdigit()), None)


def buy_scrolls():
    """Out of refresh scrolls (the Refresh tap opened the purchase popup): buy one pack - 5 Order Refresh Scrolls, 50
    gems (Nick 2026-11-03: "unlimited, buy as lacking, don't care about price"). The price is only logged; the scroll
    count must go up, else stop (a misread must never loop into spending)."""
    b = wait(r'Order Refresh Scroll', 5)
    p = next((t.strip() for x, y, w, h, t in b if 1040 < y + h // 2 < 1130 and t.strip().isdigit()), '?')
    before = scrolls()
    tap_text(r'^Purchase$', boxes=b); time.sleep(1.2); tap_wait(540, 1600); time.sleep(0.8)   # the popup stays open
    after = scrolls()
    if after is None or (before or 0) >= after: raise Stop(f'scrolls {before} -> {after} after buying a pack')
    print(f'    bought 5 refresh scrolls for {p} gems ({before} -> {after})', flush=True)
    return int(p) if p.isdigit() else 0


def fishing(cfg, orders=True):
    mn = orders and re.search(r'min_order_diamonds:\s*(\d+)', cfg)
    tap_wait(624, 1780); boxes = wait(r'Order Info', 10)
    time.sleep(0.6); back = ensure_bait(cfg) + ', '; boxes = wait(r'Order Info', 6)   # Sunday: Lucky Star only if the weekly review needs the row, else the default bait (Nick 2026-11-08)
    packs = gems = 0
    if mn:
        tap_text(r'Order Info', boxes=boxes); wait(r'Daily Order', 8)
        for row in (1, 2, 3):
            for _ in range(10):                        # ponytail: <=60 refreshes per row, only a runaway guard
                last = script('fish_orders.py', str(row), '6', mn.group(1)).split()   # confirms Order Refresh popups
                if find(ocr(), r'Order Refresh Scroll'): gems += buy_scrolls(); packs += 1; continue   # out of scrolls
                if len(last) != 2 or not last[1].isdigit() or int(last[1]) >= int(mn.group(1)): break   # done / WARN
        tap_wait(973, 270)
    got = ''
    if orders and red_dot(350, 1730, 420, 1800):          # Benefit dot (fishing-pass accounts); no pass = a $ page, no dot
        tap_wait(330, 1800); c = find(wait(r'Benefit', 6), r'^Claim Reward$')
        if c: tap_wait(*c); time.sleep(1); tap_wait(540, 120); got = 'benefit claimed, '
        tap_wait(970, 238)
    boxes = ocr()
    if find(boxes, r'Auto Fishing'): return back + got + 'auto already running'
    for _ in range(2):                                   # Start sometimes doesn't take on the first tap (Aminor 2026-10-28)
        boxes = ocr()
        if not find(boxes, r'^Start$'): tap_wait(982, 1222); boxes = wait(r'^Start$', 8)   # settings dialog
        tap_text(r'^Start$', boxes=boxes)
        try: wait(r'Auto Fishing', 4); break
        except Stop: pass
    else: raise Stop('Auto Fishing did not start')
    return back + got + (f'orders refreshed ({packs} scroll packs bought, {gems} gems), ' if mn else '') + 'auto started'


def patrol(cfg): return script('patrol.py', ACCOUNT)
def patrol_claim(cfg): return script('patrol.py', ACCOUNT, '--claim-only')


PET_ORDER = {'high_to_low': 'High to Low', 'low_to_high': 'Low to High', 'random': 'Random Selection'}
# Auto Deploy dialog check boxes -> wanted state (stamina order on, per-pet rows off, Auto-Stop on, slots fallback on)
PET_BOXES = {(898, 620): True, (898, 900): False, (898, 1210): True, (898, 1376): True}


def ticked(im, x, y): return sum(1 for dx in range(-36, 37, 4) for dy in range(-36, 37, 4)
                                 if (lambda p: p[1] > 150 and p[0] < 170 and p[2] < 120)(im.getpixel((x + dx, y + dy)))) >= 8


def pet_popup(t):
    """Round-result popup ('Champion' / 'Runner-up', 'Result of this round') pops after every round, over anything -> X."""
    if 'Deployed Sprite' in t: return False              # Auto Deploy dialog on top of it: handle the dialog first (Kong 2026-11-04 looped on the hidden X)
    if 'Runner-up' in t or 'Result of this round' in t:
        print('    pet: round popup closed', flush=True); tap(972, 548); time.sleep(0.5); return True


def pet_state():
    """After Join: 'running' (Auto Deploying), 'used' (no free attempts), 'open' (slots left) or 'full' (64/64 or a
    fight on: only the "N Arena" header reads, Dino 2026-11-03)."""
    t0, fight, t_join = time.time(), 0, time.time()
    while time.time() - t0 < 10:
        boxes = ocr(); t = joined(boxes)
        if re.search(r'attempts used up|Not enough free', t): return 'used'
        if pet_popup(t): continue
        if find(boxes, r'^Auto Deploying'): return 'running'
        m = re.search(r'Participating Pet\W*(\d+)\s*/\s*64', t)
        # count alone: the "X has deployed Y" ticker hides the Auto Deploy label in a busy arena (trace, Dino 2026-11-03)
        if m and int(m.group(1)) < 64: return 'open'
        j = find(boxes, r'^Join$', (300, 1400, 780, 1650))
        # Join tap lost: re-tap only after 2 s - a re-tap during the load lands on the pool's Deploy button (Bino)
        if j and time.time() - t_join > 2: tap(*j); fight, t_join = 0, time.time(); continue
        if j: fight = 0; time.sleep(0.3); continue
        # 64/64, or a fight (only the "N Arena" header reads): 4 reads in a row, not 1 (the arena draws in parts)
        fight = fight + 1 if 'Arena' in t else 0
        if fight >= 4: print(f'    pet: full/fight ({t[:90]})', flush=True); return 'full'
        time.sleep(0.3)
    grab().resize((540, 960)).save('v_pet_state.png'); print(f'    pet: 10 s undecided ({t[:120]})', flush=True)
    return 'full'


def pet_sprites(im, boxes, want):
    """Sprites field shows `want`? OCR misses the lone digit on some frames (Dino/Aminor 2026-11-03): try the full
    frame, then the field crop enlarged 3x."""
    if find(boxes, rf'^{want}$', (600, 400, 800, 500)): return True
    c = im.crop((580, 410, 820, 500)); return any(t.strip() == want for *_, t in ocr(c.resize((720, 270))))


def pet_dialog(sprites, order):
    """Auto Deploy -> (im, boxes, sprites ok, order ok) once the dialog has settled (an early frame missed "4"), or
    None when it doesn't open in 4 s (a fight began between Join and the tap: Chien Than 2026-11-03)."""
    tap(956, 1640); t0 = t_tap = time.time(); reopen = False
    while time.time() - t0 < 4:
        im = grab(); boxes = ocr(im); t = joined(boxes)
        if pet_popup(t): reopen = True; continue
        if 'Deployed Sprite' in t:
            ok_s = pet_sprites(im, boxes, sprites); ok_o = find(boxes, order, (540, 580, 860, 660))
            if ok_s and ok_o or time.time() - t0 > 3: return im, boxes, ok_s, ok_o
        elif reopen or time.time() - t_tap > 2: tap(956, 1640); reopen = False; t_tap = time.time()   # covered / lost
        time.sleep(0.3)
    print('    pet: Auto Deploy dialog did not open', flush=True)


def pet_back(to_join=False):
    """Back out of the arena (Auto Deploy keeps running): to the Join screen (`to_join`) or the main screen. Back from
    the pet pool goes straight to Join; only a fight asks 'Exit this match?' -> Confirm (probe, Dino 2026-11-03).
    Round popups reopen on the way (Chien Than) - closed here, plain home() could give up and stop the runner."""
    for _ in range(10):
        if is_main(): return
        boxes = ocr(); t = joined(boxes)
        if pet_popup(t): continue
        if 'Exit this match' in t: tap_text(r'^Confirm$', boxes=boxes); time.sleep(0.5); continue
        if 'Deployed Sprite' in t: tap(938, 282); time.sleep(0.6); continue   # Auto Deploy dialog: its X (back arrow is under it)
        if to_join and find(boxes, r'^Join$', (300, 1400, 780, 1650)): return
        tap(92, 1810); time.sleep(0.6)
    raise Stop(f'could not back out of the Pet Arena; screen: {joined(ocr())[:150]}')


def pet_arena(cfg):
    """Pet Arena, game days Mon-Wed, FIRST step: event hub -> Pet Arena -> Join -> Auto Deploy -> Start, left running.
    Nick 2026-11-03: be fast (the arena is busy right after the reset) - open a dropdown only when its value is wrong
    (default = 4 sprites, High to Low, kept by the game); a fight on = exit it right away, then Join again; no free
    attempts left = done for the day, however it got done."""
    if GAME_DAY.weekday() > 2: return 'SKIP closed (Mon-Wed only)'
    blk = re.search(r'^  pet_arena:.*?(?=\n  \S|\Z)', cfg, re.M | re.S).group(0)
    get = lambda k: (re.search(rf'{k}:\s*(\S+)', blk) or [None, None])[1]
    if get('strategy') != 'stamina_order': return f'MANUAL strategy {get("strategy")} (per-pet dropdowns not scripted)'
    sprites, order = get('sprites'), PET_ORDER[get('order')]
    done = 'no free attempts left - done for today'
    tap_wait(896, 340); x = None
    for _ in range(12):                                  # tab bar slides in: same x twice = settled
        x2 = hub_tabs().get('pet_arena')
        if x2 and x2 == x: break
        x = x2; time.sleep(0.3)
    if not x: raise Stop('no Pet Arena tab in the event hub')
    tap_wait(x, 1840)
    for _ in range(6):
        t0 = time.time()
        while True:                                      # Champion popup can cover Join
            boxes = ocr()
            if pet_popup(joined(boxes)): continue
            if find(boxes, r'^Join$', (300, 1400, 780, 1650)): break
            if time.time() - t0 > 15: raise Stop(f'no Join; screen: {joined(boxes)[:150]}')
            time.sleep(0.3)
        tap_text(r'^Join$', (300, 1400, 780, 1650), boxes, settle=False)
        st = pet_state()
        if st == 'used': pet_back(); return done
        if st == 'running': pet_back(); return 'Auto Deploying already on'
        if st == 'open':
            r = pet_dialog(sprites, order)
            if r: im, boxes, ok_s, ok_o = r; break
        pet_back(to_join=True)                           # fight on (also one starting just now): exit, rejoin (Nick)
    else: raise Stop('arena still full after 6 exit + rejoin')
    changed = []
    if not ok_s:   # dropdown opens upward, rows 1-4; OCR misses lone digits there -> tap the row
        tap_wait(700, 454); time.sleep(0.5); tap_wait(684, 152 + (int(sprites) - 1) * 74); changed.append(f'sprites {sprites}')
    if not ok_o:
        tap_wait(700, 620); tap_text(order, (540, 340, 860, 560), wait(order, 4, (540, 340, 860, 560))); changed.append(order)
    if changed: time.sleep(0.5); im = grab()
    for (bx, by), want in PET_BOXES.items():
        if ticked(im, bx, by) != want: tap_wait(bx, by); changed.append(f'box y{by} {"on" if want else "off"}')
    if changed:                                          # verify only what we touched
        im = grab(); boxes = ocr(im)
        bad = [f'box y{by}' for (bx, by), want in PET_BOXES.items() if ticked(im, bx, by) != want]
        if not pet_sprites(im, boxes, sprites): bad.append('sprites')
        if not find(boxes, order, (540, 580, 860, 660)): bad.append('order')
        if bad: raise Stop(f'Auto Deploy settings still wrong: {bad}')
    tap(*(find(boxes, r'^Start$', (300, 1480, 780, 1660)) or (540, 1570))); t0 = time.time()
    while True:
        t = joined(ocr())
        if 'Auto Deploying' in t: break
        if re.search(r'Not enough free|attempts used up', t): tap(938, 282); time.sleep(0.5); pet_back(); return done
        if pet_popup(t): continue
        if time.time() - t0 > 8: raise Stop('no "Auto Deploying" after Start')
        time.sleep(0.3)
    pet_back()
    return f'Auto Deploying: {sprites} sprites, {order}' + (f' (changed: {", ".join(changed)})' if changed else '')


def pet_deployments():
    """Main screen -> Pet Arena -> Achievement: "Cumulative pet deployments completed: N" (whole event, Mon-Wed)."""
    tap_wait(896, 340); wait(r'Match|Weekly', 10, (0, 1760, 1080, 1920)); time.sleep(1.2)
    x = hub_tabs().get('pet_arena')
    if not x: raise Stop('no Pet Arena tab in the event hub')
    tap_wait(x, 1840); time.sleep(1.5); pet_popup(joined(ocr()))
    tap_wait(90, 700); t = joined(wait(r'Cumulative pet deployments', 6))
    m = re.search(r'Cumulative pet deployments completed\D*?\d+ times\s*\|\s*(\d+)\s*/', t) or re.search(r'(\d+)\s*/\s*\d+', t[t.find('Cumulative'):])
    if not m: raise Stop(f'cumulative deployments unreadable: {t[:150]}')
    # milestones reached after the events step (the last deployments finish late) -> claim them here (Nick 2026-11-03)
    print(f'    pet achievement x{claim_yellow(r"^Achievement$")}', flush=True)
    tap_wait(972, 226)
    return int(m.group(1))


def pet_check(cfg):
    """LAST dailies step, Mon-Wed (Nick 2026-11-03): all 40 free Pet Arena attempts used today = the Achievement's
    cumulative deployments grew by 40 since yesterday (Bino / Tiger read 80 on Tue). Yesterday's value comes from its
    log; Monday = 0; no logged value -> 40 per earlier event day. Short -> Auto Deploy (re)started via pet_arena(),
    MANUAL so the catch-up re-checks."""
    if GAME_DAY.weekday() > 2: return 'SKIP closed (Mon-Wed only)'
    n = pet_deployments()
    prev = 0
    if GAME_DAY.weekday():
        try: logged = re.findall(r'pet deployments (\d+)', open(os.path.join(HERE, '..', 'logs', ACCOUNT, f'{GAME_DAY - datetime.timedelta(days=1)}.log')).read())
        except OSError: logged = []
        prev = int(logged[-1]) if logged else 40 * GAME_DAY.weekday()
    print(f'    pet deployments {n} (yesterday {prev}, +{n - prev} today)', flush=True)
    if n - prev >= 40: return f'all 40 free deployments used (pet deployments {n}, +{n - prev})'
    if not home(): raise Stop('lost the main screen after reading the deployments')
    r = pet_arena(cfg)
    return f'MANUAL only +{n - prev} of 40 deployments so far ({r}) - re-check in the catch-up'


def shop(cfg):
    tap_wait(100, 330); boxes = wait(r'Value Pack|Free Benefits', 10)
    got = []
    c = find(boxes, r'^Claim$', (750, 700, 1040, 880))
    if c: tap_wait(*c); time.sleep(1); tap_wait(540, 120); got.append('Free Benefits')
    tap_wait(480, 1846); wait(r'Hero Pack', 8)
    if red_dot(900, 360, 1060, 440):
        tap_wait(895, 420); time.sleep(1.5); tap_wait(540, 120); tap_wait(972, 300); got.append('Select Hero 20 gems')
    return f'claimed {got or "nothing"}'


def play_pass2(cfg):
    """After the missions: open Play Pass only if its main-screen icon has a red dot (Nick 2026-11-03); dot at
    (142-170, 430-456) on Chien Than / Dminor."""
    return play_pass(cfg) if red_dot(135, 420, 180, 465) else 'no red dot'


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
            for _ in range(10):                          # free-track Claim buttons
                c = find(ocr(), r'^Claim$', (780, 300, 960, 1750))
                if not c: break
                tap_wait(*c); time.sleep(1); tap_wait(300, 200); got.append('monthly row')
            for _ in range(10):                          # "Continue to claim" = card track: free when it has no padlock
                boxes = ocr(); c = find(boxes, r'^Continue', (780, 300, 1060, 1750))   # (Nick 2026-11-04; Cmajor: 10 shards + 2000 gold, gems same)
                if not c: break
                im = grab()                              # padlock straddles the card box's top-right corner, ~(-170,-110) from the button
                dark = sum(1 for x in range(c[0] - 206, c[0] - 136, 2) for y in range(c[1] - 149, c[1] - 79, 2) if max(im.getpixel((x, y))[:3]) < 80)
                if dark >= 10: got.append('monthly card track locked'); break
                g0 = gems(boxes); tap_wait(*c); time.sleep(1); tap_wait(300, 200)
                if gems(ocr()) < g0: raise Stop(f'monthly continue: gems dropped {g0} -> {gems(ocr())}')
                got.append('monthly card row')
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
    for _ in range(4):                                   # the cards slide in: read until every rarity label is in place (Dino/Bino/Dminor 2026-11-08: -1 tiers off a mid-slide frame)
        time.sleep(0.8); boxes = ocr()
        cs = cards(boxes, 716, 915, (192, 540, 884)) if find(boxes, r'Select Bonus Effect') else \
             cards(boxes, 429, 620, (192, 540, 884)) + cards(boxes, 1100, 1262, (150, 460, 740, 1000))
        if all(c[1] >= 0 for c in cs): break
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
    """Centre of the yellow next-floor marker on the Sanctuary map, or None. Yellow with G > 175 (the marker pulses
    255,182..235,66..99 down to ~222,190,82; the flags' darker stripes drop out) sampled every 6 px; the marker is a
    ~100-px blob = 60-100 samples over a 3x3 block of 60-px cells, a flag's gold band <= ~25 even with all 10 flags up
    (Cmajor 2026-11-08: the all-flags map read a "marker" at (739,684) -> no popup -> FAIL), so under 30 = no marker.
    No red-neighbour test any more: Lava Cave's lava is red and it threw the marker away on every account (2026-11-08)."""
    yel = lambda p: p[0] > 200 and 175 < p[1] < 250 and 40 < p[2] < 115 and p[0] - p[2] > 110
    cells = {}
    for y in range(180, 1560, 6):
        for x in range(60, 1020, 6):
            if yel(im.getpixel((x, y))): cells.setdefault((x // 60, y // 60), []).append((x, y))
    if not cells: return None
    blob = lambda c: [q for i in (-1, 0, 1) for j in (-1, 0, 1) for q in cells.get((c[0] + i, c[1] + j), [])]
    pts = blob(max(cells, key=lambda c: len(blob(c))))
    if len(pts) < 30: return None                       # Tiger's marker above the floor-10 boss = 34 samples
    return sum(x for x, _ in pts) // len(pts), sum(y for _, y in pts) // len(pts)


def sanctuary_potion():
    """Sanctuary map: Recovery Potion (top-left (88,130)) -> use one. Only "Daily usage limit reached" has been seen
    (xFaktor 2026-11-08, the day's potion used by hand), so the popup is unmapped: use it only when it names the potion,
    offers Use/Confirm and shows no purchase wording or price; anything else is closed and counts as no potion."""
    tap_wait(88, 130); time.sleep(1); boxes = ocr(); t = joined(boxes)
    if re.search(r'limit reached', t): print('    potion: daily usage limit reached', flush=True); return False
    b = find(boxes, r'^(Use|Confirm)$')
    if not b or not re.search(r'Recovery Potion|Recover', t) or re.search(r'Buy|Purchase|Diamond|Gem|\$', t):
        c = find(boxes, r'^Cancel$'); tap_wait(*(c or (540, 120)))
        print(f'    potion: not used, popup: {t[:140]}', flush=True); return False
    tap_wait(*b); time.sleep(1.2)
    if find(ocr(), r'Tap anywhere'): tap_wait(540, 120)
    print('    potion used', flush=True); return True


def sanctuary_climb():
    """Map: the next floor is the node just below the yellow marker (Cmajor, Ice Citadel 2026-10-29). Crash = instant
    win; Battle -> lineup (Quick Deploy if < 5) -> Start -> Victory Confirm -> bonus pick. A loss with the 5 main heroes ->
    Recovery Potion -> the same floor again with the 5 (Nick 2026-11-08), at most 2 potions; no potion left -> MANUAL."""
    def stable_marker():
        # the map keeps panning after a floor: a mid-pan frame put the marker at (727,458) on 4 accounts (2026-11-08,
        # settled map: (788,936)) -> 2 reads 0.5 s apart within 12 px
        m = floor_marker(grab())
        for _ in range(8):
            time.sleep(0.5); m2 = floor_marker(grab())
            if m == m2 or (m and m2 and abs(m[0] - m2[0]) + abs(m[1] - m2[1]) < 12): return m2
            m = m2
        return m
    def open_floor(m):
        for dy in (90, 120):                             # node sits ~86 px below the marker centre, the floor-10 boss ~110
            tap_wait(m[0], m[1] + dy)
            try: return wait(r'Floor \d+/10|Select Bonus Effect|Replace Bonus Effect', 4)
            except Stop: pass
    out, potions = [], 0
    for _ in range(14):                                 # 10 floors + up to 2 potion retries + pending screens
        # a bonus screen left pending by an earlier run comes back on entry and hides the marker: "all floors won" with a
        # Replace screen up on Bino/Dminor/Cmajor (2026-11-08) -> resolve it first
        boxes = ocr()
        if find(boxes, r'Select Bonus Effect|Replace Bonus Effect'): out.append(f'pending {bonus_pick()}'); continue
        # weekly "Hidden Altar" modifier card (Monday, 3 rows + Confirm, no choice) covers the map (Kong/Tiger/Chien Than 11-09)
        if find(boxes, r'Hidden Altar') and (c := find(boxes, r'^Confirm$')): tap_wait(*c); time.sleep(1); continue
        if find(boxes, r'Tap anywhere to close'): tap_wait(540, 120); time.sleep(1); continue   # floor reward still up (xFaktor 11-09)
        m = stable_marker()
        if not m: break                                  # no marker: all floors flagged
        boxes = open_floor(m)
        if boxes is None:                                # one re-read before giving up
            time.sleep(1.5); m = stable_marker()
            if not m: break
            boxes = open_floor(m)
            if boxes is None: raise Stop(f'no floor popup under the marker ({m[0]},{m[1]}); done so far: {out}')
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
            if 'Victory' not in r:                       # Defeat screen = "Challenge again" + "Tap anywhere to close", no Confirm
                for _ in range(3):                       # (Bino/Dminor/Tiger 2026-11-08: Stop -> the runner's retry re-fought); never Challenge again
                    tap_wait(540, 120); time.sleep(0.8)
                    if not find(ocr(), r'Tap anywhere to close|Challenge again'): break
                if potions < 2 and sanctuary_potion():   # Nick 2026-11-08: lost with the 5 main heroes -> potion -> again with the 5
                    potions += 1; out.append(f'floor {fl[1]} LOST -> potion, again'); continue
                out.append(f'floor {fl[1]} LOST'); return 'MANUAL ' + ', '.join(out)
            tap_text(r'^Confirm$', (200, 1300, 880, 1500)); res = 'won'
        out.append(f'floor {fl[1]} {res} {bonus_pick()}')
        if fl[1] == '10': break
    else:                                                # DoD = all floors won (Nick 2026-11-03): a marker left = not done
        if floor_marker(grab()): return 'MANUAL climb not finished: ' + ', '.join(out)
    return 'climbed: ' + ', '.join(out) if out else 'nothing to climb (all floors won)'


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
    def left(b):                                        # Vision reads a lone 0 as 'O' at full size (Cmajor 2026-11-02)
        m = re.search(r'Chances left today\W*([\dOolI]+)', joined(b))
        c = next(((x, y, w, h) for x, y, w, h, t in b if 'Chances left' in t), None)
        if not m and c:                                 # lone "1" missed at full size (Cmajor 2026-11-07, twice) -> 3x crop
            x, y, w, h = c; im = grab().crop((x + w - 80, y - 20, x + w + 180, y + h + 20))
            m = re.search(r'([\dOolI]+)\s*$', joined(ocr(im.resize((im.width * 3, im.height * 3)))))
        if not m: raise Stop(f'no chances count: {joined(b)[:150]}')
        return int(m.group(1).translate(str.maketrans('OolI', '0011')))
    n, out = left(boxes), []
    if n >= 2:                                          # first chance: run it (time cap 3m, Nick 2026-10-29), never Restart
        tap_text(r'^Start Challenge$', (200, 880, 880, 1040), boxes)
        boxes = wait(r'^Start Challenge$', 8, (0, 1700, 1080, 1920))
        tap_text(r'^Start Challenge$', (0, 1700, 1080, 1920), boxes)
        boxes = wait(r'^Confirm$', 8)   # the Tip text OCRs before its buttons finish animating (Chien Than/Dminor 11-09)
        tap_text(r'^Confirm$', (560, 1080, 960, 1250), boxes)
        t0 = time.time()
        while time.time() - t0 < 180 and not find(ocr(), r'Victory|Kill Count'): time.sleep(2)
        if not find(ocr(), r'Victory|Kill Count'):     # still fighting: Pause -> Quit Battle (counts as Victory)
            tap_wait(866, 1227); b = ocr()
            if not find(b, r'Quit Battle|Victory|Kill Count'): tap_wait(866, 1227); b = ocr()
            if not find(b, r'Victory|Kill Count'):     # fight can end right at the cap (Tiger 2026-11-06)
                tap_text(r'Quit Battle', boxes=b); wait(r'Victory|Kill Count|^Confirm$', 10)
        tap_text(r'^Confirm$', (200, 1300, 880, 1500)); boxes = wait(r'Chances left today', 10)
        n2 = left(boxes)
        if n2 != n - 1: raise Stop(f'gate chances {n} -> {n2} after a run')
        n = n2; out.append('run')
    if n >= 1:
        tap_text(r'Sweep', (850, 1000, 1060, 1110), boxes); boxes = wait(r'^Confirm$', 6)
        tap_text(r'^Confirm$', (560, 1300, 960, 1460), boxes); time.sleep(2); tap_wait(540, 120)
        n2 = left(wait(r'Chances left today', 10))
        for _ in range(8):                              # counter redraws late (Cmajor 2026-11-05: read 1, screenshot showed 0)
            if n2 == n - 1: break
            time.sleep(0.75); n2 = left(wait(r'Chances left today', 10))
        if n2 != n - 1: raise Stop(f'gate chances {n} -> {n2} after the sweep')
        out.append('sweep')
    return f'{out or "nothing left"}'


def artifact_rolls(count, got):
    """Recruit screen -> Artifact tab: Free, then Wish (stars) up to `count` rolls, Auto OFF, never the 280-gem button;
    appends 'artifact xN' (or a SKIPPED/STOPPED note) to got. Shared by the dailies (config count) and the Sunday weekly
    pass (the 'Artifact Wishing 30' row has no daily cap - Nick 2026-11-08)."""
    tap_wait(618, 1840); time.sleep(1)
    def auto_on():   # Auto = checkbox, ticked = green check at ~(866,1658); old 1-pixel test at 900 missed it (Chien Than 2026-11-04)
        im = grab().convert('RGB')
        return sum(1 for x in range(830, 900, 3) for y in range(1630, 1690, 3)
                   if (lambda q: q[1] > 150 and q[1] > q[0] + 40 and q[1] > q[2] + 40)(im.getpixel((x, y)))) >= 5
    if auto_on(): tap_wait(866, 1658); time.sleep(0.5)
    if auto_on(): got.append('ARTIFACT SKIPPED: Auto toggle stays ON')
    else:
        n = 0
        for _ in range(count):
            if auto_on(): got.append('ARTIFACT STOPPED: Auto ticked mid-run'); break
            boxes = ocr(); b = find(boxes, r'^(Free|Wish)$', (300, 1580, 780, 1700))
            if not b or find(boxes, r'^280$', (300, 1580, 780, 1700)): break     # 280 = gem price: never
            g0 = gems(boxes); tap_wait(*b); time.sleep(1.5); tap_wait(540, 120)   # fragment can sit over the button
            for _ in range(8):                       # fragment / new-artifact display (Confirm) -> back to the button
                boxes = ocr()
                if find(boxes, r'^(Free|Wish)$', (300, 1580, 780, 1700)): break
                c = find(boxes, r'^Confirm$'); tap_wait(*(c or (540, 120)))
            if gems(ocr()) < g0: raise Stop(f'artifact: gems dropped {g0} -> {gems(ocr())}')
            n += 1
        got.append(f'artifact x{n}')


def recruit(cfg, common_only=False):
    want = lambda k: int((re.search(rf'recruit:(?:\n\s+.*)*?\n\s+{k}:\s*(\d+)', cfg) or [0, 0])[1])
    tap_wait(96, 1810); wait(r'Recruitment|Recruit 1', 10)
    got = []
    tap_wait(188, 1610); time.sleep(1)
    def gems_or_none(b):
        try: return gems(b)
        except Stop: return None
    n_common = int(os.environ.get('RECRUIT_COMMON', 8 if common_only else want('common')))   # env: leftover re-runs (2026-11-08)
    for _ in range(n_common):                            # catch-up: every Free chance
        boxes = ocr(); m = re.search(r'Chances\W*(\d+)', joined(boxes))
        if not m or int(m.group(1)) == 0: break           # done for the day
        b = find(boxes, r'^Free$', (380, 1290, 700, 1420))
        # no Play Pass: "Purchase Play Pass to skip ad" + a green "▶ Recruit 1" button = a video ad per draw (xFaktor 2026-11-08, Nick: watch it)
        ad = not b and find(boxes, r'skip ad') and find(boxes, r'^Recruit 1$', (380, 1290, 700, 1420))
        if not (b or ad): break                           # cooldown
        g0 = gems_or_none(boxes); tap_wait(*(b or ad))    # draw animation can outlast 2.5 s (Chien Than/xFaktor 2026-10-29)
        if ad and not watch_ad(log=lambda t: print(t, flush=True)): raise Stop('common recruit: ad did not close')
        tap_text(r'^Confirm$', boxes=wait(r'^Confirm$', 15)); time.sleep(1); got.append('common (ad)' if ad else 'common')
        g1 = gems_or_none(ocr())
        if g0 is not None and g1 is not None and g1 < g0: raise Stop(f'common recruit: gems dropped {g0} -> {g1}')
    if want('ancestor') and not common_only:
        tap_wait(896, 1610); time.sleep(1); boxes = ocr()
        if find(boxes, r'^Free$', (150, 1290, 470, 1420)):
            tap_text(r'^Free$', (150, 1290, 470, 1420), boxes)
            tap_text(r'^Confirm$', boxes=wait(r'^Confirm$', 15)); got.append('ancestor')
    if want('artifact') and not common_only: artifact_rolls(want('artifact'), got)   # Free + Wishes (stars) up to the config count, Auto OFF (Nick 2026-11-02)
    return f'free draws {got or "none available"}'


def gems(boxes):
    """Top-left gem counter (Recruit / Artifact screens)."""
    # '100k' on rich accounts (Tiger 2026-11-08): k/M parsed - a drop under 1k then goes unseen; the 280-price / Free checks still guard
    g = [t for x, y, w, h, t in boxes if 60 <= x + w // 2 <= 260 and 40 <= y + h // 2 <= 100 and re.fullmatch(r'\d+(\.\d+)?[kKmM]?', t)]
    if not g: raise Stop(f'gem counter unreadable: {joined(boxes)[:200]}')
    return int(num(g[0]))


def hero(cfg): return script('hero.py', ACCOUNT)
def treasury(cfg): return script('treasury.py', ACCOUNT)   # King's Treasury keys, after events claims them (Nick 2026-11-10)
def tribe(cfg):
    r = script('tribe.py')
    return f'MANUAL {r}' if 'NOT SENT' in r else r      # Request didn't go out -> leftover, not OK (2026-11-07)


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


def divine(cfg):
    tap_wait(798, 1780); wait(r'Arsenal', 10)
    out = []
    tap_wait(980, 1810); time.sleep(2)
    out.append(script('veins.py'))
    tap_wait(92, 1810); wait(r'Arsenal', 8)
    if re.search(r'^\s*divine_forge:\s*false', cfg, re.M): out.append('forge off (config)')
    else:
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
    # Benefit (forging-pass accounts) AFTER the forging: its milestones ("Divine Weapon dismantled N times") count the
    # dismantles just made (Nick 2026-11-04); every Claim Reward there
    if red_dot(330, 1730, 420, 1800):                   # catch-up too (Nick 2026-11-04)
        tap_wait(309, 1810); n = 0; time.sleep(1.5)
        for _ in range(5):
            c = find(ocr(), r'^Claim Reward$')
            if not c: break
            tap_wait(*c); time.sleep(1); tap_wait(540, 120); n += 1
        tap_wait(970, 238); out.append(f'benefit x{n}' if n else 'benefit: red dot but nothing to claim')
    return ', '.join(out)


def stage(cfg):
    """Stage x adventure_stage: skull -> tab 1 = Bone Archer alone (once, it sticks) -> Start. Defeat -> "Challenge
    again" (shows ~3 s after) = back on the hero selection, lineup kept -> Start, until the target (Nick 2026-11-03: no
    close + re-open per fight). A Victory moves the stage on -> close and re-open it."""
    n, out, S = int(re.search(r'adventure_stage:\s*(\d+)', cfg)[1]), [], (0, 1700, 1080, 1920)
    tap_wait(994, 964); wait(r'^Start$', 10, S); lone_hero(tabs=True); boxes = wait(r'^Start$', 10, S)
    while True:
        tap_text(r'^Start$', S, boxes)
        res = joined(wait(r'Tap anywhere to close|Victory|Defeat', 180))
        out.append('Victory' if 'Victory' in res else 'Defeat' if 'Defeat' in res else 'done')
        if len(out) >= n: tap_wait(540, 120); break
        if out[-1] == 'Defeat':
            ca = find(wait(r'Challenge again', 6), r'Challenge again'); tap_wait(*ca)
        else:
            tap_wait(540, 120)
            if not home(): raise Stop('lost the main screen after a stage Victory')
            tap_wait(994, 964)
        boxes = wait(r'^Start$', 10, S)
    return ', '.join(out)


def grocery(cfg):
    tap_wait(994, 1625); time.sleep(1); tap_wait(900, 1230); wait(r'Daily Specials|Grocery', 10)
    out = script('grocery.py')
    tap_wait(966, 222)
    return out


def rune_tiles(im):
    """Full red (Mythic) tiles -> [(top y, cx, locked)]. Tiles = red runs at x=cx-62; the padlock sits on the tile's
    top-right corner (dark outline at cx+50..80, top-14..top+20) - checked on Tiger's 4 pages 2026-11-03: 12/12 locks."""
    red = lambda p: p[0] > 200 and p[1] < 120 and p[2] < 120
    tiles = []
    for cx in (160, 350, 540, 730, 920):
        s = None
        for y in range(320, 1580, 2):
            r = red(im.getpixel((cx - 62, y)))
            if r and s is None: s = y
            if not r and s is not None:
                # full tile only (~162 px): a cut-off top row hides its lock above the edge (Nick 2026-11-02)
                if y - s > 150 and s > 322: tiles.append((s, cx))
                s = None
    lock = lambda t, cx: any(sum(im.getpixel((x, y))[:3]) < 150 for y in range(t - 14, t + 20) for x in range(cx + 50, cx + 80))
    return [(t, cx, lock(t, cx)) for t, cx in sorted(tiles)]


def still():
    """Grab once the rune list has stopped coasting: a swipe keeps it moving ~1-2 s, and taps placed from a moving frame
    hit other tiles - locked ones (Nick 2026-11-03: "misclicked too many times on the locked runes")."""
    a = grab().crop((60, 320, 1020, 1580))
    for _ in range(12):
        time.sleep(0.3); b = grab()
        # < 2 % of samples changed = still: sparkling runes animate forever (Kong/Chien Than 2026-11-08, exact match never came)
        pa, pb = list(a.getdata())[::53], list(b.crop((60, 320, 1020, 1580)).getdata())[::53]
        if sum(x != y for x, y in zip(pa, pb)) < len(pa) // 50: return b
        a = b.crop((60, 320, 1020, 1580))
    raise Stop('rune list never stopped moving')


def rune_pick():
    """Open the Synthesize popup of an unlocked red rune -> its Synthesize button, or Stop. Never taps a padlocked tile;
    a 'Locked' reply = the detector was wrong -> stop, don't try more tiles."""
    tap_wait(994, 1625); time.sleep(1); tap_wait(900, 1775); wait(r'Backpack', 8)
    tap_wait(868, 1680)
    seen = 0
    for page in range(6):                               # unlocked reds can sit below the locked ones (Cmajor/Kong 2026-10-31)
        if page: swipe(540, 1300, 540, 700, 800)
        im = still(); tiles = rune_tiles(im); seen += len(tiles)
        free = [(t, cx) for t, cx, locked in tiles if not locked]
        if not free: continue
        t, cx = free[0]
        tap_wait(cx, t + 81)                            # tile centre
        for _ in range(8):                              # Synthesize sits lower the more stat lines the rune has (Bino)
            boxes = ocr(); s = find(boxes, r'^Synthesize$', (200, 900, 880, 1750))
            if s: return s
            if find(boxes, r'(?i)locked'): raise Stop(f'tapped a locked rune at ({cx},{t + 81}) - lock detector missed it')
            time.sleep(0.4)
        raise Stop(f'rune at ({cx},{t + 81}): no Synthesize popup')
    raise Stop(f'no unlocked red rune ({seen} red tiles seen, all locked)')


def rune(cfg):
    """Backpack -> Rune tab -> first unlocked red (Mythic) rune -> Synthesize -> Quick Equip (4 lowest-tier) ->
    Synthesize x1. Free. Mapped on the Kong instance 2026-10-29; precise picking 2026-11-03."""
    tap_wait(*rune_pick()); tap_text(r'Quick ?Equip', (250, 1600, 580, 1720), wait(r'Quick ?Equip', 6))
    boxes = wait(r'^Synthesize$', 4, (650, 1600, 1000, 1720))
    if not find(boxes, r'^[xX]1$', (60, 1600, 200, 1720)): raise Stop('rune: multiplier is not x1')
    im = grab()   # grey Synthesize = Quick Equip found < 4 runes of that quality (Chloe 2026-11-10: 2) -> nothing to do
    if sum(1 for x in range(700, 950, 6) for y in range(1640, 1700, 6)
           if (lambda p: max(p) - min(p) > 40)(im.getpixel((x, y)))) < 20:
        grab().save('v_rune.png'); tap_wait(972, 560); time.sleep(0.8); tap_wait(972, 238)
        return 'SKIP Synthesize greyed: < 4 runes of that quality (v_rune.png)'
    tap_text(r'^Synthesize$', (650, 1600, 1000, 1720), boxes)
    res = wait(r'Congratulations', 8); r = next((b[4] for b in res if 'Rune' in b[4]), 'rune')
    tap_text(r'^Confirm$', boxes=res); time.sleep(0.8); tap_wait(972, 560); time.sleep(0.8); tap_wait(972, 238)
    return f'synthesized -> {r}'


SHOP_TABS = {'sanctuary': (452, False), 'tribe': (732, False), 'ruins': (980, False), 'realm': (604, True)}  # x, after tab-bar swipe


def coin(im, x0, x1, cy):
    """Mean colour of a coin icon's coloured pixels (left of its number): the paw / edges / background average out.
    A fixed sample point hit the icon edge and skipped Realm tile 4 every day since late Oct (24x); whole icon: all 12
    Realm tiles within 2-4 of the balance icon (Dino 2026-11-03)."""
    px = [p for p in (im.getpixel((x, y)) for x in range(x0, x1, 2) for y in range(cy - 16, cy + 17, 2)) if max(p) - min(p) > 80]
    return [sum(p[i] for p in px) // len(px) for i in range(3)] if px else [0, 0, 0]


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
            bb = next((b for b in boxes if b[0] < 300 and 350 < b[1] < 430 and re.fullmatch(r'[\d.]+[kKmM]?', b[4])), None)
            bal = bb and num(bb[4])
            bx, by = (163, 413, 663, 913)[(n - 1) % 4], (893, 1249, 1605)[(n - 1) // 4]
            region = (bx - 125, by - 40, bx + 125, by + 40)
            if find(boxes, r'Sold', region): out.append(f'{tab} {n} sold out'); continue
            pb = next((b for b in boxes if region[0] < b[0] + b[2] // 2 < region[2] and region[1] < b[1] + b[3] // 2 < region[3]
                       and re.fullmatch(r'[\d.]+[kKmM]?', b[4])), None)
            price = pb and num(pb[4])
            if bal is None or price is None: raise Stop(f'{tab} {n}: balance/price unreadable ({bal}, {price})')
            if not near(coin(im, pb[0] - 70, pb[0] - 12, pb[1] + pb[3] // 2), coin(im, bb[0] - 66, bb[0] - 8, bb[1] + bb[3] // 2), 35):
                out.append(f'{tab} {n} SKIPPED: not priced in the shop coin'); continue
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
    react); top Claim row ≈ (860,672) claims all rows; chests above the level labels (y≈510) glow when reachable; tabs
    Daily (300,1686) / Weekly (778,1688), each tab's red dot at its top-right (Weekly ≈ (972,1636)), hidden while selected.
    Both tabs are always opened (2026-11-04: the Weekly tab was gated on its dot, which the daily chest reward popup still
    dimmed -> every account skipped 4 claimable weekly rows, Nick). Ends with the dot check = the step's DoD."""
    if not red_dot(1000, 1545, 1080, 1615): return "no red dot"   # menu icon dot (Mission / Lobby / Backpack)
    tap_wait(994, 1625); wait(r'^Mission$', 6); time.sleep(1.2)   # side menu slides in: read the position once settled
    m = find(ocr(), r'^Mission$')
    if not m: raise Stop('Mission entry not in the side menu')
    tap_wait(m[0] - 120, m[1] - 30); wait(r'Daily Mission', 10)
    out = []
    TABS = {'daily': (300, r'Daily Mission', (40, 80, 120, 160)), 'weekly': (778, r'Weekly Mission', (45, 90, 135, 180))}
    dot = {'daily': (420, 1595, 540, 1665), 'weekly': (898, 1595, 1018, 1665)}   # x+120..x+240 (Weekly dot y 1618-1650 Aminor)
    def no_popup():                                       # reward popups ("Tap anywhere to close") dim the whole dialog
        for _ in range(8):
            if not find(ocr(), r'Tap anywhere'): return True
            tap_wait(540, 240); time.sleep(0.8)
        return False
    for tab, (x, title, levels) in TABS.items():
        if tab == 'weekly':
            no_popup(); tap_wait(x, 1688); time.sleep(1)
            if not find(ocr(), title): tap_wait(x, 1688); wait(title, 6)   # tab tap eaten by a late popup -> once more
        for _ in range(4):                                # top row Claim claims every claimable row (Kong); repeat while one shows
            c = find(ocr(), r'^Cla[il]m$', (700, 560, 1060, 780))   # top row only — never scroll, never GO
            if not c: break
            tap_wait(*c); time.sleep(1.2); tap_wait(540, 240); out.append(f'{tab} rows'); no_popup()
        im = grab()                                       # reachable chests glow yellow (~350 px vs ~50 locked, Kong)
        glow = [lv for lv, cx in zip(levels, (423, 592, 762, 930))
                if sum(1 for y in range(330, 470, 3) for x in range(cx - 70, cx + 70, 3)
                       if (lambda p: p[0] > 235 and p[1] > 215 and p[2] < 160)(im.getpixel((x, y)))) > 150]
        if glow:                                          # one reachable chest claims every reachable one
            cx = dict(zip(levels, (423, 592, 762, 930)))[glow[0]]
            tap_wait(cx, 420); time.sleep(1.2); tap_wait(540, 240); out.append(f'{tab} chests {glow}'); no_popup()
    # DoD: no tab dot left. The selected tab hides its own dot: read Daily's from the Weekly tab, then switch and read Weekly's.
    left = ['daily'] if red_dot(*dot['daily']) else []
    tap_wait(300, 1688); time.sleep(1)
    if red_dot(*dot['weekly']): left.append('weekly')
    if left: grab().save('v_daily_mission.png'); out.append(f'{left} tab still has a red dot (v_daily_mission.png)')
    tap_wait(972, 238)
    return ('MANUAL ' if left else '') + f'{out or "nothing"}'


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

def storm_rewards():
    """Storm arena Rewards (96,880), called by storm() on its arena screen: OCR the rank banner above the shield, tap
    only that rank's row in the panel. Lower rows only if the red dot survives (rank jumped since the last claim)."""
    im = grab(); p = im.getpixel((400, 1580))
    if not (p[0] > 200 and p[1] > 150 and p[2] < 80):    # storm.py left a popup / other screen -> reopen Storm
        home(); storm_arena()
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


def arena_claims():
    """Called by arena() on its screen: weekly win chests 10/20/35/50 at y≈210; reached (wins >= N) and no green check -> tap, dismiss."""
    boxes = ocr()
    if not find(boxes, r'Winnings'):                     # arena.py left another screen -> reopen Arena
        home(); tap_wait(100, 1280); boxes = wait(r'Winnings', 10)
    w = next((int(b[4]) for b in boxes if b[4].strip().isdigit() and b[0] < 240 and 260 < b[1] < 340), None)
    if w is None: return 'win count unreadable; no chest tapped'   # a lone '0' after the weekly reset isn't OCR'd (xFaktor 2026-11-02); claims only, never fail Arena for it
    im, got = grab(), []
    for n, x in ((10, 376), (20, 536), (35, 696), (50, 864)):
        green = sum(1 for yy in range(200, 290, 3) for xx in range(x - 40, x + 40, 3)
                    if (lambda p: p[1] > 170 and p[0] < 150 and p[2] < 120)(im.getpixel((xx, yy))))
        if w >= n and green < 20:
            tap_wait(x, 210); time.sleep(1.2); tap_wait(540, 120); got.append(n)
    return f'wins {w}, chests claimed {got}' if got else f'wins {w}, nothing to claim'


def open_canyon():
    """Main -> Tribe -> Canyon map. The 8 h occupation ends with a *Resource* popup on entry ("resources gathering is
    now completed", Collect Time 08:00:00) — "Attempts" shows behind it, so close it first: Confirm, dismiss (Nick, 2026-10-31)."""
    tap_wait(448, 1780); time.sleep(1.5); tap_wait(540, 1090); boxes = wait(r'Attempts', 10)
    for _ in range(2):
        if not find(boxes, r'gathering is now completed|^Resource$'): return
        c = find(boxes, r'^Confirm$'); tap_wait(*(c or (540, 1460))); time.sleep(1); boxes = ocr()
        if find(boxes, r'Tap anywhere'): tap_wait(540, 120); boxes = ocr()   # gains popup; a low tap could hit a platform
    raise Stop('Canyon Resource popup did not close')


def canyon_rewards():
    """Called by canyon() on the fresh Canyon map: always open Rewards (88,745) — no red-dot gate, the dot was never
    seen on 11-05 — and Claim Reward while its button isn't grey (95,96,95 = nothing reached). Returns the points read
    on the panel as evidence."""
    if find(ocr(), r'Congratulations|Tap anywhere'): tap_wait(540, 120); time.sleep(1)  # late gains popup ate the Rewards tap (Cmajor 11-09)
    tap_wait(88, 745); boxes = wait(r'Points Reward', 10); n = 0
    pts = next((t for x, y, w, h, t in boxes if 240 <= x + w // 2 <= 420 and re.fullmatch(r'\d{3,6}', t.strip())), '?')
    for _ in range(6):
        im = grab(); c = find(ocr(im), r'^Claim Reward$')
        if not c: break
        if not near(im.getpixel((c[0], c[1] + 40)), (255, 182, 16), 30): break   # grey button = no tier reached (text pixels mislead: Cmajor 11-05)
        tap_wait(*c); time.sleep(1.2); tap_wait(540, 1880); n += 1
    tap_wait(972, 240); wait(r'Attempts', 10)            # back on the map
    return f'points {pts}, claimed x{n}'


def canyon(cfg):
    """Take a new EMPTY spot by the day's rule (scripts/canyon.py), then the Points Rewards — occupying earns the points
    (Nick 2026-11-04). No empty one -> MANUAL (helper may beat a Sentinel, never a player)."""
    if NOW.weekday() == 0 and 6 <= NOW.hour < 17: return 'SKIP closed until Mon 17:00'
    open_canyon()
    if canyon.taken: out = 'spot taken earlier this run'  # the runner's retry re-occupied after a rewards FAIL (Dino 11-05)
    else:
        try: out = script('canyon.py', ACCOUNT)
        except Stop as e:
            if 'exit 2' not in str(e): raise
            out = 'MANUAL no empty platform (attack choice)'
        canyon.taken = out.startswith('occupied')
    time.sleep(1)                                        # the points land after the Occupy popup closes
    return f'{out}; rewards: {canyon_rewards()}'         # Rewards is fixed HUD: same spot wherever canyon.py left the map


canyon.taken = False


HUB_TABS = {r'^Wish': 'wish_festival', r'^Pet|^Arena$': 'pet_arena', r'^Golden': 'golden_woods', r'^Draws|^7777': '7777', r'^Match': 'match_event', r'^Weekly': 'weekly_event', r'^Limited': 'limited_recruitment'}


def hub_tabs():
    """Event hub bottom tabs -> {tab: label x}. The set changes with the events, so tabs shift: find them by label
    (Kong instance 2026-10-29: 4 tabs, Wish Festival at x=480 where fixed coords said Pet Arena)."""
    tabs = {}
    for x, y, w, h, t in ocr():
        for pat, tab in HUB_TABS.items():
            if y > 1800 and re.search(pat, t) and tab not in tabs: tabs[tab] = x + w // 2
    return tabs


def golden_woods(left):
    """Golden Woods (2026-11-03): free collects only - Exploration Quest (1 Claim = all quest rows, Treasury Keys),
    Sign-In Rewards (today's yellow Claim; never "Continue to claim" = $ Deluxe), Woods Expedition gift icon (top-left,
    20 gems). Never King's Treasury (Shuffle Cards spends keys), Expedition Draw / Daily Pack ($). Sub-tab red dots sit
    ~63 px right of the sub-tab centre, y~190; the tab's own dot sticks (keys to shuffle) - judged by these."""
    got, dot = [], lambda x: red_dot(x + 40, 165, x + 90, 215)
    def sub(x, title):                                   # a tap during the reward close is ignored (Kong 2026-11-03)
        for _ in range(2):
            tap_wait(x, 300)
            try: wait(title, 4); return True
            except Stop: pass
        left.append(f'golden_woods {title}'); return False
    deluxe = False
    for name, x, title in (('quests', 412, r'Exploration Quest'), ('sign-in', 660, r'Sign-In Rewards')):
        if sub(x, title) and claim_yellow(title, dismiss=(540, 960)): got.append(name)
    b = ocr()       # still on Sign-In: its dot sticks on "Continue to claim" ($ Deluxe) once the free Claim is done (2026-11-07)
    if find(b, r'Sign-In Rewards') and find(b, r'^Continue') and not find(b, r'^Claim$'): deluxe = True
    if sub(908, r'Woods Expedition') and red_dot(115, 490, 155, 530):
        tap_wait(88, 550); close_reward(); got.append('expedition gift')
    if dot(412) or (dot(660) and not deluxe) or red_dot(115, 490, 155, 530): left.append('golden_woods')
    return [f'golden woods {g}' for g in got]


def limited_recruitment():
    """Limited Recruitment (cycle event, mapped on Tiger 2026-11-10): Hero Trial = free unlimited boss Challenge, daily
    chests by single highest damage (5 AM reset) - Challenge once when its button has a dot, then claim the chest dots;
    Limited Merchant Free Recruit Pack (10 tickets). Never Recruit (spends tickets) or Training Program / $ packs."""
    got = []
    tap_wait(412, 280); wait(r'Single Highest', 6)
    if red_dot(670, 1540, 730, 1600):                    # Challenge's dot = not fought since the reset
        tap_wait(540, 1620); wait(r'^Start$', 8); tap_wait(540, 1810)
        tap_text(r'^Confirm$', (300, 1150, 780, 1300), wait(r'^Confirm$', 180, (300, 1150, 780, 1300)))
        wait(r'Single Highest', 8); got.append('hero trial challenge')
    n = 0
    for x in (280, 452, 624, 796, 968):                  # damage chests 100k..800k, dot ~36 px right-above each
        if red_dot(x + 10, 1305, x + 65, 1355): tap_wait(x, 1356); close_reward(); n += 1
    got.append(f'hero trial chests x{n}')
    tap_wait(908, 280); wait(r'Limited Offer', 6); got.append(f'limited free pack x{claim_yellow(r"Limited Offer")}')
    return got


def unmapped_tabs(im=None):
    """Event hub tab labels (their 1st line) that match no HUB_TABS pattern and carry a red dot."""
    im = im or grab()
    return [t for x, y, w, h, t in ocr(im) if 1800 < y < 1848 and len(t.strip()) > 2
            and not any(re.search(p, t) for p in HUB_TABS) and red_dot(x + w // 2 + 30, 1720, min(x + w // 2 + 95, 1080), 1795, im)]


def close_reward(dismiss=(540, 1880)):
    """Reward popup -> tap its own "Tap anywhere to close" line (the popup centre is the reward icon: tapping it didn't
    close Golden Woods' Sign-In reward, 2026-11-03); `dismiss` only when that line isn't shown."""
    b = wait(r'Tap anywhere|Congratulations', 4)
    tap_wait(*(find(b, r'Tap anywhere') or dismiss))
    for _ in range(6):
        if not find(ocr(), r'Tap anywhere to close'): return
        time.sleep(0.4)


def claim_yellow(title, dismiss=(540, 1880)):
    """Tap every exact 'Claim'/'Free' whose button is the yellow (255,182,16) - never 'Claim More', grey (locked) or
    a $/gem button - dismissing each reward; stops when none is left or the dialog `title` is gone. No reward popup
    after a tap (e.g. a no-pass account's video ad) -> Stop."""
    n = 0
    for _ in range(12):
        im = grab(); boxes = ocr(im)
        if not find(boxes, title): break
        c = next(((x + w // 2, y + h // 2) for x, y, w, h, t in boxes if t.strip() in ('Claim', 'Free')
                  and near(im.getpixel((x - 12, y + h // 2)), (255, 182, 16), 30)), None)
        if not c: break
        tap_wait(*c); close_reward(dismiss); n += 1
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


# Floating Realm Pack (Nick, 2026-11-03): daily in its event week, Mon-Thu (Preparation + Battle; none in the truce).
# key -> (row title, button text, paid with, max cost). $ buttons open a Tip "Pay with N Stargems" -> Confirm.
REALM_PACKS = {'free': ('Free Pack', r'^(Free|Claim)$', None, 0),
               'support': ('Support Pack', r'^\D?80$', 'gems', 80),
               'motivation': ('Motivation Pack', r'^\D?\d{2,3}$', 'gems', 400),     # 400 on Dminor
               'value': ('Value Pack', r'^\$0\.99$', 'stargems', 60),               # Tip: 60 Stargems (Dminor)
               'joy': ('Joy Pack', r'^\$4\.99$', 'stargems', 300)}                  # ponytail: 300 = 5x Value, unseen


def balance(box):
    """A currency counter top left of the Pack popup - gems (60,40,260,100), Stargems (300,40,500,100) - OCR'd alone:
    the whole-screen OCR glued '620' to the title behind it ('6201ng Realm', Aminor 2026-11-03)."""
    c = grab().crop(box); c = c.resize((c.width * 2, c.height * 2))
    d = [t for *_, t in ocr(c) if t.isdigit()]
    if not d: raise Stop(f'balance unreadable at {box}')
    return int(d[0])


def drag(y0, y1, x=540):
    """Scroll by holding the finger still before lifting: no fling. A plain 680 px swipe glided ~1300 px and an OCR of
    the still-moving list put taps at stale spots (FR Pack, Dminor 2026-11-03). Moves ~60 px less than y0-y1 (slop)."""
    ys = ' '.join(str(y) for y in range(y0 - 100, y1, -100)) + f' {y1}'
    subprocess.run(['adb', '-s', D, 'shell', f'input motionevent DOWN {x} {y0}; for y in {ys}; do input motionevent MOVE {x} $y; '
                    f'done; sleep 0.6; input motionevent UP {x} {y1}'])


def settle(limit=4):
    """Wait until the screen stops moving (a scrolled list keeps gliding after the swipe)."""
    prev, t0 = thumb(grab()), time.time()
    while time.time() - t0 < limit:
        time.sleep(0.3); cur = thumb(grab())
        if diff(cur, prev) < 1: return
        prev = cur


def realm_buy(btn, price, cur, cap):
    """One pack row's button: Sold Out / not the expected price / balance short -> report; else tap, check any Tip's
    amount against cap (Cancel if over or unreadable) -> Confirm -> reward popup. Returns the result text."""
    if any('Sold Out' in s for *_, s in btn): return 'already'
    hit = next((c for c in btn if re.search(price, c[2])), None)
    if not hit: return f'NOT bought: button {[c[2] for c in btn]}'
    if cur:
        have = balance((60, 40, 260, 100) if cur == 'gems' else (300, 40, 500, 100))
        if have < cap: return f'NOT bought: {cur} {have} < {cap}'
    tap_wait(hit[0], hit[1]); time.sleep(1)
    b = ocr(); r = joined(b); paid = hit[2]
    if find(b, r'^Tip$') and find(b, r'^Confirm$'):
        tip = joined([x for x in b if 640 < x[1] < 1100])  # the Tip's own text, not the price buttons behind it
        num = re.sub(r'\D', '', hit[2])                 # gem packs: the Tip must name the button's own price
        n = re.search(r'Pay with (\d+) Stargems', tip) if cur == 'stargems' else re.search(rf'\b{num}\b', tip)
        if not n or int(n[1] if cur == 'stargems' else n[0]) > cap:
            tap_text(r'^Cancel$', boxes=b); return f'NOT bought: Tip {tip[:80]!r} (cap {cap})'
        paid = f'{hit[2]} = {n[1]} Stargems' if cur == 'stargems' else hit[2]
        tap_text(r'^Confirm$', boxes=b); time.sleep(1); b = ocr(); r = joined(b)
    if not re.search(r'Tap anywhere|Congratulations', r):
        if find(b, price, (700, 600, 1080, 1560)): return f'NOT bought: the {hit[2]} tap had no effect'
        raise Stop(f'unexpected screen after the {hit[2]} tap: {r[:200]}')
    close_reward()
    sold = find(ocr(), r'Sold Out', (700, hit[1] - 80, 1080, hit[1] + 80))
    return f'bought ({paid}{"" if sold else ", not Sold Out after?"})'


def tribe_pack(cfg):
    """Tribe event = the 3rd right-column banner on the main screen: Floating Realm / Tribe Clash / Crystal Throne, one at a
    time, never overlapping (Nick 2026-11-07). Tribe Clash + Crystal Throne: Pack (980,1610) -> the free 20-gem pack
    (Limited 1, yellow Claim/Free) once a day; never the $ packs, Treasures or Enter. Floating Realm -> realm_packs.
    Uncollected on every account until Nick spotted it on Crystal Throne (2026-11-07). Done = that row reads Sold Out."""
    pat = r'^(Crystal Throne|Tribe Clash)'
    p = find(ocr(), pat, (600, 400, 1080, 900))
    if not p: time.sleep(3); p = find(ocr(), pat, (600, 400, 1080, 900))
    if not p: return 'SKIP no Tribe Clash / Crystal Throne banner'
    tap_wait(*p); wait(r'Participat|^Enter$|Treasure', 10)
    tap_wait(980, 1610); wait(r'Limited', 6)
    n = claim_yellow(r'Limited')
    for _ in range(6):                                   # the button redraws late after the reward closes (Kong 2026-11-07)
        sold = find(ocr(), r'^Sold Out$', (700, 700, 1000, 1000))   # Crystal Throne y~812, Tribe Clash Free y~934
        if sold: break
        time.sleep(0.5)
    tap_wait(972, 228)
    if not sold: raise Stop(f'free pack not Sold Out after {n} claim(s)')
    return f'free pack x{n}'


def realm_packs(cfg):
    """Floating Realm banner -> Pack -> the account's floating_realm_packs, each 1/day (REALM_PACKS: price read off
    the button, balance off the counter, a Tip's amount checked before Confirm)."""
    m = re.search(r'^\s+floating_realm_packs:\s*\[(.*?)\]', cfg, re.M)
    want = [k.strip() for k in m.group(1).split(',') if k.strip()] if m else []
    if [k for k in want if k not in REALM_PACKS]: raise Stop(f'unknown floating_realm_packs {want}')
    if not want: return 'SKIP no floating_realm_packs'
    p = find(ocr(), r'Floating Realm', (600, 400, 1080, 900))
    if not p: time.sleep(3); p = find(ocr(), r'Floating Realm', (600, 400, 1080, 900))   # loads late after a boot (Tiger)
    if not p: return 'SKIP no Floating Realm banner (not its event week)'
    for _ in range(2):                                   # the banner tap can be ignored; xFaktor ignored every tap until
                                                         # a game restart (boot.sh), Aminor too (2026-11-03)
        tap_wait(*p); time.sleep(1); b = ocr()
        # Claim day opens under a "Match Result" ranking popup (Chien Than 2026-11-06)
        for _ in range(3):                               # then "Finals Concluded"; tap the title, not its own line
            if find(b, r'Tap anywhere'): tap_wait(540, 120); b = ocr()
        if find(b, r'^Enter$|^Pack$'): break
    else: raise Stop('Floating Realm screen did not open (banner stuck? restart the game: boot.sh <idx>)')
    pk = find(b, r'^Pack$')
    if not pk: return 'SKIP no Pack button (truce)'
    tap_wait(*pk)
    if find(wait(r'Daily Special|Not in Purchase Period', 8), r'Not in Purchase Period'):
        return 'SKIP Not in Purchase Period (claim day)'
    for _ in range(2): swipe(540, 900, 540, 1500, 400)   # it reopens where it was left (Motivation hid under the banner)
    settle()
    out, todo = [], list(want)
    for i in range(4):
        # top: Free + Support; one 2-row drag shows Motivation, Value and Joy together (Nick, 2026-11-03)
        if i: drag(1400, 640 if i == 1 else 1100); settle()
        b = ocr()
        for k in list(todo):
            title, price, cur, cap = REALM_PACKS[k]
            t = find(b, rf'^{title}$', (0, 600, 600, 1560))   # above y 600 the "Value Deal" banner covers the list
            if not t or t[1] + 250 > 1560: continue      # its button sits ~166 px below the title
            btn = [(x + w // 2, y + h // 2, s) for x, y, w, h, s in b if x > 700 and t[1] + 80 < y + h // 2 < t[1] + 250]
            todo.remove(k); out.append(f'{k} {realm_buy(btn, price, cur, cap)}')
            b = ocr()
        if not todo: break
    tap_wait(972, 228)
    r = ', '.join(out + [f'{k} not found' for k in todo])
    return f'MANUAL {r}' if 'NOT' in r or 'not found' in r or '?' in r else r


def events(cfg):
    """Event hub (1st banner) bottom tabs with a red dot. Scripted: Wish Festival sign-in/gift, Weekly Event Free
    Benefits, Match Event milestones, 7777 daily Claim, Golden Woods Exploration Quest claims. Other tabs with a dot -> MANUAL. Never Again / Open All / draws / Tribe Clash (its dot never clears)."""
    tap_wait(896, 340); wait(r'Match|Weekly', 10, (0, 1760, 1080, 1920))
    out, left = [], []
    time.sleep(1.5); tabs = hub_tabs()
    # The SELECTED tab hides its own red dot and the hub opens on the last-used tab, so that tab was always skipped
    # (Dino's Match Event, 2026-11-01). Read with 2 different tabs selected; every tab shows its dot in one of them.
    read = lambda: {t: red_dot(x + 30, 1720, min(x + 95, 1080), 1795) for t, x in tabs.items()}
    # Always 2 DIFFERENT tabs: picking "tabs without a dot" picked only the hidden (selected) tab itself when every other
    # tab had a dot -> Weekly Event Free Benefits missed on xFaktor + Bino (2026-11-04).
    dots = read()
    for t in list(tabs)[:2]:
        tap_wait(tabs[t], 1840); time.sleep(1.2)
        dots = {k: v or d for (k, v), d in zip(dots.items(), read().values())}
    print(f'    hub tabs (red dot): {dots}', flush=True)   # 'nothing claimed' couldn't tell no tab / no dot / missed (2026-11-01)
    # a tab nobody mapped is invisible to hub_tabs(): Golden Woods' quests went uncollected on every account (2026-11-03)
    new_tabs = unmapped_tabs()
    if new_tabs: left += [f'unmapped tab {t}' for t in new_tabs]
    for tab, x in tabs.items():
        # 7777: always look - its dot read False on Aminor/Bino/Cmajor with the daily Claim still up (Nick 2026-11-02)
        if not dots[tab] and tab != '7777': continue
        tap_wait(x, 1840); time.sleep(1.2)
        if tab == 'match_event':
            n = 0
            for sub in ((160, 320), (400, 310)):         # the week's 2 sub-events (Canyon Warrior / Heroic Trial, Arena King / Lord's Challenge)
                tap_wait(*sub); time.sleep(1)
                for _ in range(25):                      # top row's Claim rolls to the next milestone; 8 left 2 on Dino (2026-11-01)
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
        elif tab == 'pet_arena':
            time.sleep(1); pet_popup(joined(ocr()))       # round-result popup over the lobby
            if red_dot(105, 290, 160, 345):              # Pack: Free Pack (20 gems, Limited 1) - never the $ packs (2026-11-03)
                tap_wait(90, 365); wait(r'^Pack$', 6); out.append(f'pet free pack x{claim_yellow(r"^Pack$", dismiss=(540, 960))}')
                for _ in range(3):                       # X, until the Pack popup is really gone
                    tap_wait(972, 236); time.sleep(0.6)
                    if not find(ocr(), r'Value Offer'): break
            if red_dot(100, 620, 160, 680):              # Achievement: free deployment-milestone Claims (2026-11-02)
                tap_wait(90, 700); wait(r'^Achievement$', 6); out.append(f'pet achievement x{claim_yellow(r"^Achievement$")}')
                tap_wait(972, 226)
        elif tab == 'golden_woods': out += golden_woods(left)
        elif tab == 'limited_recruitment': out += limited_recruitment()
        elif tab == 'weekly_event':                      # 2nd sub-tab (Wish Merchant / Pet Shop / Recruit Store): Free Benefits
            tap_wait(410, 240); time.sleep(1); out.append(f'weekly free x{claim_yellow(r"Free Benefits")}')
        else: left.append(tab)
        if red_dot(x + 30, 1720, min(x + 95, 1080), 1795) and tab not in left and tab not in ('7777', 'wish_festival', 'golden_woods'):
            left.append(tab)                             # sticky dots: 7777 after its daily Claim, Wish Festival's Treasure Vault (coin draws, never)
    r = ', '.join(out) or 'nothing claimed'
    return f'MANUAL {r}; red dots left: {left}' if left else r


# --- Weekly missions, Sunday pass (Nick 2026-11-08): accounts/weekly.yaml top-down; the four rows no daily step makes were
# mapped on Kong (ui-routine "Weekly Missions"). Draw x10 counts 10, Lucky Star bait only on Sunday, Statue last resort (Nick).
WEEKLY_KEY = {'sanctuary': 'Secret Sanctuary', 'poseidon': 'Poseidon', 'treasure_draw': 'Draw Treasure', 'gate': 'Gate of Darkness',
              'canyon': 'Canyon', 'tribe_trial': 'Tribe Trial', 'trials': 'Land of Trials', 'speed_patrol': 'Speed Patrol',
              'match_points': 'Match Points', 'hero_level': 'Leveled', 'match': 'Match Challenges', 'stage': r'Stage \d', 'tower': 'Tower',
              'gear': 'Enhanced Equipment', 'artifact_wish': 'Artifact Wishing', 'honor': 'Honor', 'statue_upgrade': 'Upgrade Statue',
              'lucky_stars': 'Lucky Star', 'adv_recruit': 'Advanced Recruitment', 'grocery_gems': 'Diamonds', 'statue_blessing': 'Blessing',
              'ascend': 'Ascended'}
BAIT_TILES = [(198, 1120), (426, 1120), (654, 1120), (908, 1120), (198, 1340), (426, 1340), (654, 1340), (908, 1340)]   # Bait grid, tile 3 = Lucky Star


def weekly_list():
    """accounts/weekly.yaml -> [(id, do)] in Nick's priority order (top-down)."""
    s = open(os.path.join(HERE, '..', 'accounts', 'weekly.yaml')).read()
    return [(m.group(1), m.group(2) == 'true') for m in re.finditer(r'id:\s*(\w+),.*?do:\s*(true|false)', s)]


def weekly_rows(boxes):
    """One Weekly-tab page -> {row name: (done, total)}: each 'n/m' progress box + the row's text 50-135 px above it
    (a 2-line name keeps its first line; the previous row sits ~190 px up)."""
    out = {}
    for x, y, w, h, t in boxes:
        m = re.fullmatch(r'(\d+)/(\d+)', t.strip()); cy = y + h // 2
        if not m or not 560 < cy < 1580: continue
        name = ' '.join(tt for xx, yy, ww, hh, tt in sorted(boxes, key=lambda b: (b[1], b[0]))
                        if 50 < cy - (yy + hh // 2) < 135 and xx + ww // 2 < 760 and not re.fullmatch(r'\d+', tt.strip()))
        if name: out[name] = (int(m.group(1)), int(m.group(2)))
    return out


def weekly_read():
    """Main -> Mission popup -> Weekly tab -> (points, {name: (done, total)}) over every page; leaves the popup open."""
    tap_wait(994, 1625); wait(r'^Mission$', 6); time.sleep(1.2); m = find(ocr(), r'^Mission$')
    if not m: raise Stop('Mission entry not in the side menu')
    tap_wait(m[0] - 120, m[1] - 30); wait(r'Daily Mission', 10)
    tap_wait(778, 1688); time.sleep(1); boxes = wait(r'Weekly Mission', 6)
    p = [t for x, y, w, h, t in boxes if 100 < x + w // 2 < 260 and 400 < y + h // 2 < 540 and t.strip().isdigit()]
    rows, prev = {}, None
    for _ in range(8):                                    # slow swipes; a page equal to the last = the list's end
        r = weekly_rows(ocr()); rows.update(r)
        if r and set(r) == prev: break
        prev = set(r); swipe(540, 1400, 540, 850, 1500); time.sleep(1.8)
    return (int(p[0]) if p else -1), rows


def weekly_treasure(need):
    """Recruit > Treasure: one Draw x10 (= 10 draws, Nick) if the Lucky Coins balance on screen covers its price."""
    tap_wait(96, 1810); wait(r'Recruitment|Recruit 1', 10); time.sleep(0.8); tap_wait(976, 1800); boxes = wait(r'Blind Box', 8)
    bal = [t for x, y, w, h, t in boxes if x + w // 2 < 320 and y + h // 2 < 110 and re.fullmatch(r'[\d.]+[kKmM]?', t.strip())]
    pr = [re.search(r'\d{4,6}', t).group() for x, y, w, h, t in boxes if x + w // 2 > 600 and 1170 < y + h // 2 < 1270 and re.search(r'\d{4,6}', t)]
    if not bal or not pr: raise Stop(f'treasure: balance/price unreadable: {joined(boxes)[:160]}')
    bal, price = int(num(bal[0])), int(pr[0])
    if bal < price: return f'treasure: {bal} Lucky Coins < {price}, no draw'
    tap_wait(770, 1220); wait(r'Tap anywhere|Confirm|Congratulations|Obtain', 20)
    for _ in range(8):                                    # result cards -> back on the Blind Box screen
        b = ocr()
        if find(b, r'Blind Box') and not find(b, r'Tap anywhere|Congratulations'): break
        c = find(b, r'^Confirm$'); tap_wait(*(c or (540, 120))); time.sleep(1)
    b2 = [t for x, y, w, h, t in ocr() if x + w // 2 < 320 and y + h // 2 < 110 and re.fullmatch(r'[\d.]+[kKmM]?', t.strip())]
    after = int(num(b2[0])) if b2 else -1
    if after < 0 or after > bal - price // 2: raise Stop(f'treasure: Draw x10 tapped but the balance did not drop ({bal} -> {after})')
    return f'treasure: Draw x10 (-{price} Lucky Coins, {bal} -> {after})'


def weekly_honor(need):
    """Side menu > Lobby > Honor Bonus: Upgrade (15000 gold + 1 medal each) `need` times while both costs are covered."""
    tap_wait(994, 1625); wait(r'^Mission$', 6); time.sleep(1.2); l = find(ocr(), r'^Lobby$')
    if not l: raise Stop('Lobby entry not in the side menu')
    tap_wait(l[0] - 120, l[1] - 30); wait(r'Honor Bonus', 10); time.sleep(0.8)
    done = []
    for _ in range(need):
        boxes = ocr()
        costs = sorted((x + w // 2, t) for x, y, w, h, t in boxes if 1600 < y + h // 2 < 1700 and '/' in t)   # gold, medal
        if len(costs) < 2: raise Stop(f'honor: costs unreadable: {joined(boxes)[:160]}')
        have = [int(num(c.split('/')[0].strip())) for _, c in costs[:2]]; cost = [int(num(c.split('/')[1].strip())) for _, c in costs[:2]]
        if have[0] < cost[0] or have[1] < cost[1]: done.append(f'stop: gold {have[0]}/{cost[0]}, medals {have[1]}/{cost[1]}'); break
        before = ' '.join(t for x, y, w, h, t in boxes if 1440 < y + h // 2 < 1580)   # level + progress bar
        tap_wait(380, 1808); time.sleep(1.2)                                           # never (724,1808) = Upgrade Lv.1
        c = find(ocr(), r'^Confirm$')
        if c: tap_wait(*c); time.sleep(1)
        after = ' '.join(t for x, y, w, h, t in ocr() if 1440 < y + h // 2 < 1580)
        if after == before: done.append('no change after Upgrade'); break
        done.append(f'+1 ({after.strip()[:40]})')
    return 'honor: ' + ', '.join(done)


def set_bait(target):
    """On the fishing screen: Bait tab -> make `target` the bait in use (Swap) and verify. The grid reorders itself - the
    bait in use jumps to tile 1 (Kong 2026-11-08: Lucky Star 1st, Shrimp 3rd) - so tiles are found by the description
    title, never by position."""
    title = lambda boxes=None: next((t.strip() for x, y, w, h, t in (boxes or ocr()) if 300 < x + w // 2 < 760 and 370 < y + h // 2 < 450), '')
    def in_use():
        boxes = ocr(); iu = find(boxes, r'In use')
        if iu: tap_wait(*min(BAIT_TILES, key=lambda p: abs(p[0] - iu[0]) + abs(p[1] - iu[1]))); time.sleep(0.7); boxes = ocr()
        return title(boxes)
    b = find(ocr(), r'^Bait$', (880, 1380, 1080, 1540)); tap_wait(*(b or (986, 1459))); wait(r'^Swap$', 6); time.sleep(0.8)
    now = in_use()
    if now == target: tap_wait(968, 240); return f'bait {target} (in use)'
    for p in BAIT_TILES:
        tap_wait(*p); time.sleep(0.7)
        if title() == target: break
    else: tap_wait(968, 240); raise Stop(f'bait {target!r} not in the grid')
    tap_wait(539, 1557); time.sleep(1.2)
    if find(ocr(), r'^Swap$'): raise Stop('bait: Swap did not close the Bait popup')
    tap_wait(*(b or (986, 1459))); wait(r'^Swap$', 6); time.sleep(0.8); got = in_use(); tap_wait(968, 240)   # verify
    if got != target: raise Stop(f'bait: swapped but {got!r} is in use, not {target!r}')
    return f'bait swapped to {target} (was {now or "?"})'


def bait_default(cfg):
    m = re.search(r'^\s+bait:\s*([^#\n]+)', cfg, re.M)           # fishing: bait: <name>  (optional)
    return m.group(1).strip().strip('"') if m else 'Basic Bait'   # the game's default; Nick 2026-11-08: never Shrimp unless configured


def weekly_plan_file(): return f'/tmp/miniheroes-state/{ACCOUNT}-{GAME_DAY}.weekly_plan'


def ensure_bait(cfg):
    """Fishing screen, every start: Lucky Star when Sunday's weekly review found the 50-stars row necessary for 180, else
    the account's default bait (`fishing.bait`, default Basic Bait) - Nick 2026-11-08: stars only when we really have to, Shrimp only if configured."""
    plan = weekly_plan_file()
    stars = GAME_DAY.weekday() == 6 and os.path.exists(plan) and open(plan).read().strip() == 'stars'
    return set_bait('Lucky Star' if stars else bait_default(cfg))


def weekly_review(cfg):
    """Sunday catch-up, FIRST step (Nick 2026-11-08): read the Weekly tab and decide whether the Lucky Star row is needed -
    i.e. the other open doable rows cannot close the gap to 180 by themselves. The plan steers today's fishing bait."""
    if GAME_DAY.weekday() != 6: return 'SKIP not Sunday'
    pts, rows = weekly_read(); tap_wait(972, 238)
    prog = lambda key: next(((d, t) for name, (d, t) in rows.items() if re.search(key, name)), None)
    open_rows = [mid for mid, do in weekly_list() if do and (p := prog(WEEKLY_KEY[mid])) and p[0] < p[1]]
    others = [m for m in open_rows if m != 'lucky_stars']
    need = 'lucky_stars' in open_rows and pts + 10 * len(others) < 180
    os.makedirs('/tmp/miniheroes-state', exist_ok=True); open(weekly_plan_file(), 'w').write('stars' if need else 'nostars')
    return f'{pts} pts, {len(rows)} rows read; open doable: {", ".join(open_rows) or "none"}; Lucky Stars {"NEEDED -> stars bait today" if need else "not needed -> default bait"}'


def weekly_statue(need):
    """Hero > Statue: Level Up while the Power Required bar is full (one level per full bar), at most `need` times."""
    tap_wait(274, 1780); wait(r'^Statue$', 8); tap_wait(635, 1848); wait(r'Power Required', 8); time.sleep(0.8)
    done = 0
    for _ in range(need):
        boxes = ocr(); t = joined(boxes)
        bar = [tt for x, y, w, h, tt in boxes if 1430 < y + h // 2 < 1510 and re.search(r'\d+/\d+', tt)]
        lv = re.search(r'Lv\.(\d+)', t)
        if not bar or not lv: raise Stop(f'statue: bar/level unreadable: {t[:160]}')
        have, req = map(int, re.search(r'(\d+)/(\d+)', bar[0]).groups())
        if have < req: return f'statue: +{done}, bar {have}/{req} not full'
        tap_wait(540, 1589); time.sleep(1.5)
        if find(ocr(), r'Tap anywhere|Congratulations'): tap_wait(540, 120); time.sleep(0.8)
        lv2 = re.search(r'Lv\.(\d+)', joined(ocr()))
        if not lv2 or int(lv2.group(1)) <= int(lv.group(1)): return f'statue: +{done}, Level Up did not raise the level ({lv.group(1)})'
        done += 1
    return f'statue: +{done} level(s)'


def weekly(cfg):
    """Sunday pass (Nick 2026-11-08): read the Weekly tab, then down accounts/weekly.yaml: Draw x10, Honor Upgrades, Artifact
    Wishes; claim; still under 180 -> the deferred rows in list order (Statue Level Up, Lucky Star bait - only when we really
    have to) and claim again. Rows the daily steps produce can't be pushed past their daily caps -> listed as short."""
    if GAME_DAY.weekday() != 6: return 'SKIP not Sunday'
    pts, rows = weekly_read(); tap_wait(972, 238)
    prog = lambda key: next(((d, t) for name, (d, t) in rows.items() if re.search(key, name)), None)
    out, short, deferred = [f'{pts} pts, {len(rows)} rows read'], [], []
    out.append('new rows: ' + ', '.join(f'{m} {prog(WEEKLY_KEY[m]) or "?"}' for m in ('treasure_draw', 'honor', 'artifact_wish', 'lucky_stars', 'statue_upgrade')))
    if pts < 180:
        for mid, do in weekly_list():
            p = prog(WEEKLY_KEY[mid])
            if not p:
                if do: out.append(f'{mid}: row not read')
                continue
            d, t = p
            if d >= t or not do: continue
            if mid in ('statue_upgrade', 'lucky_stars'): deferred.append((mid, t - d)); continue
            if mid not in ('treasure_draw', 'honor', 'artifact_wish'): short.append(f'{mid} {d}/{t}'); continue
            if not home(): raise Stop('lost the main screen in the weekly pass')
            if mid == 'treasure_draw': out.append(weekly_treasure(t - d))
            elif mid == 'honor': out.append(weekly_honor(t - d))
            else:
                got = []; tap_wait(96, 1810); wait(r'Recruitment|Recruit 1', 10); artifact_rolls(t - d, got); out.append('artifact wishes: ' + ', '.join(got))
    if not home(): raise Stop('lost the main screen in the weekly pass')
    claims = [str(daily_mission(cfg))]
    if deferred and pts < 180:
        if not home(): raise Stop('lost the main screen in the weekly pass')
        pts2, _ = weekly_read(); tap_wait(972, 238); out.append(f'{pts2} pts after claims')
        if pts2 < 180:
            for mid, need in deferred:                    # list order (Nick: Statue 17th, Lucky Stars 18th)
                if not home(): raise Stop('lost the main screen in the weekly pass')
                if mid == 'statue_upgrade': out.append(weekly_statue(need))
                else: tap_wait(624, 1780); wait(r'Order Info', 10); time.sleep(0.6); out.append(set_bait('Lucky Star') + ' (50 casts to go)')
            if not home(): raise Stop('lost the main screen in the weekly pass')
            claims.append(str(daily_mission(cfg)))
    tag = 'MANUAL ' if any(c.startswith('MANUAL') for c in claims) else ''
    return tag + '; '.join(out) + (f'; short (daily caps): {", ".join(short)}' if short else '') + f'; claims: {" / ".join(claims)}'


# catch-up (.claude/skills/catch-up): Fishing auto only, Arena, Storm, Veins + Forge (no Benefit), Patrol Claim All,
# Arena again, Tribe chat Request/Assist, Common Recruitment, Daily Mission, Fishing order rewards
CATCHUP = [('weekly_review', weekly_review),   # Sundays: the Weekly tab first - decides today's fishing bait (Nick 2026-11-08)
           ('fishing_auto', lambda c: fishing(c, orders=False)), ('arena', arena), ('storm', storm),   # fishing first: Auto runs during the rest (Nick, 2026-10-29)
           ('veins_forge', divine), ('patrol_claim', patrol_claim), ('arena2', arena),
           # Request every run, morning too: on cooldown the tap does nothing (Nick 2026-11-08, undoes the 11-07 morning skip)
           ('tribe_chat', lambda c: script('tribe.py', '--chat-only')), ('common_recruit', lambda c: recruit(c, common_only=True)),
           ('canyon', canyon),
           ('events', events), ('fishing_rewards', fishing_rewards), ('daily_mission', daily_mission),  # missions always last (Nick, 2026-10-29); FR packs: dailies only (Nick 2026-11-03)
           ('play_pass2', play_pass2),   # after the missions: the run's activity unlocks new Play Pass claims (Nick 2026-11-03)
           ('pet_check', pet_check)]    # Mon-Wed: re-check all 40 free Pet Arena attempts used (Nick 2026-11-03)
CATCHUP_MANUAL = []
def seq(*parts):
    """One runner step made of sub-steps (fn, config key or None), back to main between them. MANUAL/SKIP tags of a
    part carry over to the whole step; a part whose config key is off is left out."""
    def run(cfg):
        out = []
        for fn, key in parts:
            if not enabled(cfg, key): continue
            if out and not home(): raise Stop('lost the main screen between sub-steps')
            out.append(str(fn(cfg)))
        tag = next((t for t in ('MANUAL', 'SKIP') if any(o.startswith(t) for o in out)), '')
        return (tag + ' ' if tag and not out[0].startswith(tag) else '') + '; '.join(out)
    return run


# Daily run order — reviewed with Nick 2026-10-31 (dailies-sequence.md): Arena before and after Patrol (patrol loot
# refills tickets) and again after Adventure; Storm/Arena/Tribe/Grocery carry their own reward claims; Adventure top
# to bottom (Trials first); Canyon inside Tribe; Daily Mission always last.
ORDER = [('pet_arena', pet_arena), ('fishing', fishing), ('arena', arena), ('patrol', patrol), ('arena2', arena),
         ('storm', storm), ('shop', shop), ('play_pass', play_pass),
         ('trials', trials), ('tower', tower), ('sanctuary', sanctuary), ('gate', gate), ('beast', beast),
         ('arena3', arena), ('recruit', recruit), ('hero', hero),
         ('tribe', seq((tribe, None), (canyon, 'canyon_clash'))), ('divine', divine),
         ('stage', stage), ('patrol_claim', patrol_claim), ('rune', rune),
         ('grocery', seq((grocery, 'grocery_free_chests'), (grocery_buy, 'grocery_buy'))),
         ('events', events), ('treasury', treasury), ('tribe_pack', tribe_pack), ('realm_packs', realm_packs), ('fishing_rewards', fishing_rewards), ('daily_mission', daily_mission),
         ('weekly', weekly),   # Sundays only: the weekly-missions pass (Nick 2026-11-08)
         ('play_pass2', play_pass2)]   # after the missions: re-check Play Pass red dots (Nick 2026-11-03)
# pet_check: catch-up only (removed from the dailies, Nick 2026-11-04: Auto Deploy isn't done by then)
# config key that must be present / truthy for a step to run
KEY = {'pet_arena': 'pet_arena', 'storm': None, 'arena': 'arena', 'arena2': 'arena', 'fishing': 'fishing', 'patrol': 'patrol', 'patrol_claim': 'patrol',
       'shop': 'shop_freebies', 'play_pass': 'play_pass_claims', 'play_pass2': 'play_pass_claims', 'pet_check': 'pet_arena', 'tower': 'tower_of_the_throne', 'sanctuary': 'secret_sanctuary',
       'gate': 'gate_of_darkness', 'beast': 'beast_realm', 'trials': 'land_of_trials', 'recruit': 'recruit', 'hero': 'hero_upgrade',
       'tribe': 'tribe', 'divine': 'divine_weapon', 'stage': 'adventure_stage', 'grocery': None, 'arena3': 'arena',
       'daily_mission': None, 'fishing_rewards': 'fishing', 'fishing_auto': 'fishing', 'veins_forge': 'divine_weapon',
       'tribe_chat': 'tribe', 'common_recruit': 'recruit',
       'events': None, 'treasury': None, 'weekly': None, 'weekly_review': None, 'tribe_pack': 'shop_freebies', 'realm_packs': 'floating_realm_packs', 'canyon': 'canyon_clash', 'rune': 'rune_synthesis', 'grocery_buy': 'grocery_buy'}


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
    os.environ['ACCOUNT'] = ACCOUNT                     # flow.tickets_full runs arena.py for it
    cfg = open(os.path.join(HERE, '..', 'accounts', ACCOUNT + '.yaml')).read()
    out = os.environ.get('OUT') or f'/tmp/miniheroes-{NOW:%F}/{ACCOUNT}'
    os.makedirs(out, exist_ok=True); os.chdir(out)
    if only: left = []                                 # single steps: report only their own leftovers
    elif catch_up: left = list(CATCHUP_MANUAL)
    else: left = []
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
    try:
        if not home(): print('FAIL start: not on the main screen'); return 1
    except RuntimeError as e: print(f'FAIL start: device unreachable ({e}) - instance stopped?'); return 1

    def step(name, fn):
        """Run one step; True = OK/SKIP/MANUAL, False = FAIL, None = lost the main screen."""
        t0, ok = time.time(), True
        try:
            try: r = fn(cfg)
            except Exception as e:                       # tickets-full popup: tickets spent, step's screen gone -> redo once
                if 'MATCH_FULL' not in str(e): raise
                print(f'    {name}: {e}', flush=True)
                if not home(): raise
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
        # one retry, right away: most FAILs are transient (2026-10-29: 18 of 19 passed on a re-run; steps re-read their
        # counters, so a retry never double-spends). In place, not at the end: Chien Than's Speed Patrol ran after Daily
        # Mission and Arena (2026-11-01), so its mission points and patrol Arena tickets came too late.
        if r is False: print(f'--- retrying {name}', flush=True); r = step(name, fn)
        if r is None: print('LEFT FOR HELPER:', ', '.join(left + failed + [name])); return 1
        if not r: failed.append(name)
    left += failed
    print('LEFT FOR HELPER:', ', '.join(left))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
