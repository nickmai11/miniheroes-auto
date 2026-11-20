#!/usr/bin/env python3
# Babysit the game's own auto stage climb (occasional, not part of the dailies): auto stops after X-40 (3-wave boss)
# -> close the reward, Next chapter, open the stage, Start; Defeat screen up 3 s -> Challenge again.
# usage: scripts/climb_stage.py <account>... [--minutes N] [--stop-next-chapter]   |   scripts/climb_stage.py <account> --swap | --record | --apply
# --apply: put the yaml stage_lineups back on all 3 tabs (after a SWAP LINEUPS FAILED), then Start.
# --record [--no-start]: from any screen -> fresh battle setup, read each tab's deployed heroes by face (green checks), write
# stage_lineups, then Start (unless --no-start). Grid rows are found by measuring each slow-drag scroll.
# Accounts = accounts/<account>.yaml names; the game is moved to the stage if it's elsewhere.
# --stop-next-chapter (Nick, 2026-11-06 "stop at next stage 1"): after X-40, Next chapter but no Start -> the account
# waits on (X+1)-1, line `STOPPED at …`, no longer watched; all stopped -> exit 0 "all stopped". Don't pass it again next call.
# Runs N minutes (default 9, fits one Bash call) then exits 0 "still climbing" — just run it again.
# Heroes are found by their face (scripts/hero_faces.py, Nick 2026-11-14), never by grid position; an unknown face -> the
# hero list is learnt (new skin) and the read/deploy redone once. stage_lineups = hero ids (sea_captain).
# Lost the same stage 3x in a row -> swap the losing wave's team with the next tab (stage_lineups heroes in the account
# yaml, which is rewritten), max 3 swaps per stage, then exit 2 (look by hand).
# exit 1 = a step's screen didn't show or a stage didn't change for 4 min (climb_stage_<name>.png in /tmp).
# Seen 2026-10-31 (Bino/Dino): after a Challenge again the game sometimes goes to the next chapter itself.
import json, os, re, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(HERE)
M = '/Applications/MuMuPlayer Pro.app/Contents/MacOS/mumu-cli'
args = sys.argv[1:]
minutes = float(args[args.index('--minutes') + 1]) if '--minutes' in args else 9
accts = [a for i, a in enumerate(args) if not a.startswith('--') and (i == 0 or args[i - 1] != '--minutes')]
sys.path.insert(0, HERE)
import accounts
devs = {}
for _, a, inst, port in accounts.rows(accts):
    if not port: sys.exit(f'{a}: instance {inst} not running')
    devs[a] = f'127.0.0.1:{port}'
    subprocess.run(['adb', 'connect', devs[a]], capture_output=True)   # drops after the Mac sleeps (2026-11-01)
os.environ['D'] = next(iter(devs.values()))
sys.path.insert(0, HERE)
import flow, hero_faces, tap as T

gd = subprocess.run('TZ=UTC date -v-5H +%F', shell=True, capture_output=True, text=True).stdout.strip()


def log(a, msg):
    line = f"{time.strftime('%F %T')} [climb_stage] {msg}"
    print(a, line, flush=True)
    os.makedirs(f'{R}/logs/{a}', exist_ok=True)
    open(f'{R}/logs/{a}/{gd}.log', 'a').write(line + '\n')


def step(a, xy, pat, to=20):
    r = subprocess.run(['python3', f'{HERE}/tap.py', *([xy] if xy else []), '-o', f'/tmp/climb_stage_{a}.png', '-w', '270', '--until-text', pat,
                        '--timeout', str(to)], env={**os.environ, 'D': devs[a]}, capture_output=True, text=True)
    if r.returncode: log(a, f'FAIL waiting {pat!r} after {xy}: {r.stdout.strip()[-300:]}'); sys.exit(1)
    return r.stdout


FIGHT = r'Victory|Defeat|Lv\.|x2|ATK'  # any of these = a battle (or its result) is on


TAB = {1: 380, 2: 540, 3: 700}
COLX = [136, 336, 536, 736, 936]
ROW1, PITCH = 1255, 232          # card centers at the top of the grid: row r at ROW1 + (r-1)*PITCH


def adb(d, *a): subprocess.run(['adb', '-s', d, 'shell', 'input', *map(str, a)])


def gray(): return __import__('numpy').asarray(T.grab().convert('L'), dtype=float)[:, ::4]


def to_top(d):
    """Swipe down until the grid stops moving (long hero lists need many swipes: Chien Than 2026-11-01)."""
    prev = None
    for _ in range(15):
        adb(d, 'swipe', 540, 1150, 540, 1700, 300); time.sleep(0.8); g = gray()[1150:1570]
        if prev is not None and abs(g - prev).mean() < 2: return
        prev = g
    raise RuntimeError('hero grid never reached the top')


def scroll(d):
    """Slow-drag the grid up ~170-200 px and return how far it really moved. Rows repeat every PITCH, so a shift
    near/over a row is ambiguous (fixed y and 230-px drags put wrong heroes in, Chien Than/Dino 2026-11-01): the
    short drag keeps the true shift the only match in 20-300; a poor best match raises instead of guessing. Limit 16
    (was 12; Bino/pawn1 11-14 stopped at 12-13): every card is now checked by its face, so a near-miss can't misplace a hero."""
    b = gray(); adb(d, 'swipe', 540, 1450, 540, 1330, 2000); time.sleep(1.2); a = gray()
    if abs(a[1150:1570] - b[1150:1570]).mean() < 2: return 0   # grid end
    err = {s: abs(a[1150:1230] - b[1150 + s:1230 + s]).mean() for s in range(20, 301, 2)}
    s = min(err, key=err.get)
    if err[s] > 16: raise RuntimeError(f'grid scroll not measurable (best {s}px, err {err[s]:.0f})')
    return s


def grid_pass(d, fn):
    """Call fn({row: y}) for each grid row once, top down, until fn returns True (-> True) or the grid ends (-> False)."""
    to_top(d); off, done, retries = 0, set(), 0
    for _ in range(80):   # ~70 heroes = 14 rows, ~1.3 rows per scroll, + fling resets
        vis = {r: ROW1 + (r - 1) * PITCH - off for r in range(1, 40) if r not in done and 1180 < ROW1 + (r - 1) * PITCH - off < 1520}
        if vis and fn(vis): return True
        done |= set(vis)
        try: s = scroll(d)
        except RuntimeError:   # a slow drag sometimes flings far past 300 px (Chien Than 7-20, 2026-11-02): from the top again
            retries += 1
            if retries > 5: raise
            to_top(d); off = 0; continue
        if not s: return False
        off += s
    raise RuntimeError('hero grid never ended')


def faces(vis):
    """{name: (x, y)} of the recognised cards in the visible rows (hero_faces.ident: by face, never by position)."""
    im = T.grab(); out = {}
    for y in vis.values():
        for x in COLX:
            n = hero_faces.ident(hero_faces.face(im, x, y - 105))[0]
            if n: out[n] = (x, y)
    return out


def deploy(a, want):
    """Battle setup, the want tabs already recalled: tap each wanted hero on its tab, found by face (Nick 2026-11-14:
    faces, not grid positions). One not found -> learn the hero list (new skin?), recall, all again. -> {tab: not found}."""
    d = devs[a]
    for attempt in (0, 1):
        left = {t: set(v) for t, v in want.items()}
        def place(vis):
            found = faces(vis)
            for t, names in left.items():
                hits = [n for n in names if n in found]
                if hits: step(a, f'{TAB[t]},1088', 'Start')
                for n in hits: adb(d, 'tap', *found[n]); time.sleep(0.6)
                names -= set(hits)
            return not any(left.values())
        if grid_pass(d, place): return {}
        if attempt: break
        log(a, f'heroes not found by face {dict((t, sorted(v)) for t, v in left.items() if v)} -> learn the hero list (new skin?)')
        relearn(a)   # ends on a fresh setup = the saved lineups again
        for t in want: step(a, f'{TAB[t]},1088', 'Start'); step(a, '1000,1080', 'Start')
    return {t: sorted(v) for t, v in left.items() if v}


def relearn(a):
    """Hero list -> save unknown faces (hero_faces.py learn), back to a fresh battle setup."""
    to_main(a)
    r = subprocess.run(['python3', f'{HERE}/hero_faces.py', 'learn'], env={**os.environ, 'D': devs[a]}, capture_output=True, text=True)
    log(a, 'learn: ' + ' | '.join(l for l in r.stdout.splitlines() if 'saved' in l or 'faces in' in l))
    hero_faces._T = None
    to_main(a); step(a, '994,964', r'^Start$|\| Start \|')


def swap(a, k=1):
    """Losing wave = the open tab of the Challenge-again setup. Fresh setup from the main screen (Challenge-again
    edits aren't saved), recall both tabs, deploy each other's heroes (found by face), re-read, rewrite the yaml, Start.
    Power is never a check (Nick 2026-11-06: power doesn't matter) - only which heroes sit on which tab."""
    T.D = flow.D = devs[a]; d = devs[a]
    im = T.grab()
    won = lambda t: sum(1 for dx in range(-40, 41, 4) for dy in range(-25, 26, 4)
                        if (lambda p: p[1] > 170 and p[0] < 160 and p[2] < 120)(im.getpixel((TAB[t] + dx, 1088 + dy)))) >= 6
    w = next((t for t in (1, 2, 3) if not won(t)), 3)   # first tab without the green check = the wave we lose
    o = (w + k - 1) % 3 + 1   # 1st swap on a stage: next tab, 2nd: the other one (Dino flip-flopped 1<->2, 2026-11-01)
    o = o % 3 + 1 if o == w else o
    log(a, f'losing wave {w} (tabs won: {[t for t in (1, 2, 3) if won(t)]}) -> swap with {o}')
    step(a, '80,1810', 'Adventure', 10); time.sleep(1); step(a, '994,964', r'^Start$|\| Start \|')
    # the yaml goes stale when Nick edits lineups: it put a team-1 hero into the swap and the "Move hero?" Tip
    # blocked every tap after it (Chien Than 2026-11-02) -> read the real lineups first, swap nothing if unsure
    teams = read_lineups(a)
    if any(len(teams[t]) != 5 or '?' in ''.join(teams[t]) for t in (w, o)): log(a, f'SWAP LINEUPS: lineups unreadable {teams}, nothing changed'); sys.exit(2)
    for t in (w, o): step(a, f'{TAB[t]},1088', 'Start'); step(a, '1000,1080', 'Start')
    want = {**teams, w: teams[o], o: teams[w]}
    miss = deploy(a, {w: teams[o], o: teams[w]})
    if miss: log(a, f'SWAP LINEUPS FAILED: not found by face {miss} - left on setup'); sys.exit(2)
    got = read_lineups(a)
    if any(sorted(got[t]) != sorted(want[t]) for t in (1, 2, 3)):
        log(a, f'SWAP LINEUPS FAILED: tabs read {got}, want {want} - left on setup'); sys.exit(2)
    write_lineups(a, want)
    log(a, f'swapped lineups {w}<->{o}: {want}, yaml updated')
    if '--no-start' not in args: step(a, '540,1806', FIGHT, 30)


def to_main(a):
    """Main screen; a running fight has no back arrow -> wait for its result and close it first."""
    d = devs[a]
    if 'x2' in flow.joined(flow.ocr(T.grab())):
        step(a, '', r'Victory|Defeat', 300); time.sleep(1); adb(d, 'tap', 540, 1880); time.sleep(1.5)
    r = subprocess.run(['python3', '-c', 'import flow; print(flow.home())'], cwd=HERE, env={**os.environ, 'D': d}, capture_output=True, text=True)
    if 'True' not in r.stdout: log(a, 'could not reach the main screen'); sys.exit(1)


def apply(a):
    T.D = flow.D = devs[a]; d = devs[a]
    y = open(f'{R}/accounts/{a}.yaml').read()
    teams = {int(k): v.split(', ') for k, v in re.findall(r'^\s+(\d): \{heroes: \[([^\]]*)\]', y, re.M)}
    if len(teams) != 3: log(a, 'APPLY: no stage_lineups heroes in the yaml (old cells format?) - run --record'); sys.exit(2)
    to_main(a)
    step(a, '994,964', r'^Start$|\| Start \|')
    for t in (1, 2, 3): step(a, f'{TAB[t]},1088', 'Start'); step(a, '1000,1080', 'Start')
    miss = deploy(a, teams)
    if miss: log(a, f'APPLY FAILED: not found by face {miss} - left on setup'); sys.exit(2)
    got = read_lineups(a)
    if any(sorted(got[t]) != sorted(teams[t]) for t in (1, 2, 3)):
        log(a, f'APPLY FAILED: tabs read {got}, yaml {teams} - left on setup'); sys.exit(2)
    log(a, f'applied yaml lineups {teams}')
    step(a, '540,1806', FIGHT, 30)


def checked(im, x, y0, y1):
    """Green deploy check on the card at column x between y0..y1."""
    return sum(1 for dx in range(-50, 51, 6) for y in range(y0, y1, 6)
               if (lambda p: p[1] > 170 and p[0] < 160 and p[2] < 120)(im.getpixel((x + dx, y)))) >= 8


def read_lineups(a, learned=False):
    """On a fresh battle setup: each tab's deployed heroes (green checks) by face. Scans until each tab has 5 (or the
    grid ends). An unrecognised face -> learn the hero list once (new skin?) and read again; still unknown -> '?rNcM'."""
    d = devs[a]
    teams = {1: [], 2: [], 3: []}
    def clean():
        multi = {c for t in teams for c in teams[t] if sum(c in v for v in teams.values()) > 1}   # green card art (pawn1 r4c2)
        return {t: [c for c in v if c not in multi] for t, v in teams.items()}
    def read(vis):
        for t in (1, 2, 3):
            step(a, f'{TAB[t]},1088', 'Start'); time.sleep(0.6); im = T.grab()
            teams[t] += [hero_faces.ident(hero_faces.face(im, x, yc - 105))[0] or f'?r{r}c{c + 1}'
                         for r, yc in vis.items() for c, x in enumerate(COLX) if checked(im, x, yc - 75, yc + 75)]
        return all(len(v) >= 5 for v in clean().values())
    grid_pass(d, read)
    got = clean()
    unk = [n for v in got.values() for n in v if n.startswith('?')]
    if unk and not learned:
        log(a, f'unrecognised faces {unk} -> learn the hero list (new skin?)')
        relearn(a); return read_lineups(a, True)
    return got


def record(a):
    T.D = flow.D = devs[a]
    to_main(a)
    step(a, '994,964', r'^Start$|\| Start \|')
    teams = read_lineups(a)
    bad = [t for t in teams if len(teams[t]) != 5]
    bad += [t for t in teams if t not in bad and '?' in ''.join(teams[t])]
    if bad: log(a, f'record: tabs {bad} not 5 recognised heroes: {teams} - not written'); sys.exit(1)
    write_lineups(a, teams)
    log(a, f'recorded stage_lineups {teams}')
    if '--no-start' in args: return
    step(a, '540,1806', FIGHT, 30)
    log(a, 'started the stage')


def write_lineups(a, teams):
    path = f'{R}/accounts/{a}.yaml'; y = open(path).read()
    y = re.sub(r'\n  stage_lineups:.*?(?=\n  \S|\Z)', '', y, flags=re.S)
    y = y.rstrip('\n') + '\n  stage_lineups:   # see bino.yaml; recorded by climb_stage.py --record ' + time.strftime('%F') + '\n' + ''.join(
        f'    {t}: {{heroes: [{", ".join(teams[t])}], good_for: ""}}\n' for t in (1, 2, 3))
    open(path, 'w').write(y)


def start(a):
    """Not on a stage battle/result/setup (Nick used the account) -> main screen (flow.home) -> skull -> Start."""
    T.D = flow.D = devs[a]
    for _ in range(5):   # between fights the screen can be blank/loading (pawn1 2026-11-01): look a few times
        t = flow.joined(flow.ocr(T.grab()))
        if re.search(r'Stage: ?\d+-\d+|x2|Victory|Defeat|Challenge|Next Stage|Tap anywhere', t): return
        time.sleep(1.5)
    r = subprocess.run(['python3', '-c', 'import flow; print(flow.home())'], cwd=HERE, env={**os.environ, 'D': devs[a]},
                       capture_output=True, text=True)
    if 'True' not in r.stdout: log(a, f'FAIL: could not reach the main screen ({r.stdout.strip()} {r.stderr.strip()[-200:]})'); sys.exit(1)
    step(a, '994,964', r'^Start$|\| Start \|')
    step(a, '540,1806', FIGHT, 30)
    log(a, 'was off the stage screen -> main -> started the stage')


if '--record' in args:
    for a in accts: record(a)
    sys.exit(0)
if '--apply' in args:   # put the yaml stage_lineups back on all 3 tabs (after a failed swap), then Start
    for a in accts: apply(a)
    sys.exit(0)
if '--swap' in args: swap(accts[0]); sys.exit(0)   # one swap now (account on a Challenge-again setup) [--no-start]
for a in devs: start(a)
seen, losses, stopped = {}, {}, set()
# swaps per (account, stage) survive across calls (Boudior 2026-11-14: 4 swaps on 4-15 over 3 calls, cap never hit)
SW = '/tmp/climb_stage_swaps.json'
swaps = json.load(open(SW)) if os.path.exists(SW) else {}
end = time.time() + minutes * 60
while time.time() < end:
    for a, d in devs.items():
        if a in stopped: continue
        T.D = flow.D = d
        b = flow.ocr(T.grab()); t = flow.joined(b)
        st = re.search(r'Stage:? ?(\d+)-(\d+)', t)
        if 'Defeat' in t and flow.find(b, r'Challenge again'):
            time.sleep(3); b = flow.ocr(T.grab()); ca = flow.find(b, r'Challenge again')
            if ca:
                stage = st and st.group(0)
                n = losses[a][1] + 1 if losses.get(a, ('',))[0] == stage else 1
                losses[a] = (stage, n)
                log(a, f'Defeat {n} on {stage} -> Challenge again')
                if n >= 3:  # Nick 2026-10-31: 3 losses in a row -> swap lineups (stage_lineups in the account yaml)
                    step(a, f'{ca[0]},{ca[1]}', r'^Start$|\| Start \|', 30)
                    k = f'{a} {stage}'; swaps[k] = swaps.get(k, 0) + 1; json.dump(swaps, open(SW, 'w'))
                    if swaps[k] > 3: log(a, f'SWAP LINEUPS: {stage} still lost after 3 swaps, left on the battle setup'); sys.exit(2)
                    swap(a, swaps[k]); losses.pop(a); seen.pop(a, None); continue
                step(a, f'{ca[0]},{ca[1]}', 'Start|' + FIGHT, 30)
                if flow.find(flow.ocr(T.grab()), r'^Start$'): step(a, '540,1806', FIGHT, 30)
                seen.pop(a, None); continue
        if st and seen.get(a, ('',))[0] != st.group(0): seen[a] = (st.group(0), time.time())
        elif a in seen and time.time() - seen[a][1] > 240: log(a, f'STUCK on {seen[a][0]} 4 min: {t}'); sys.exit(1)
        if st and st.group(2) == '40' and 'Stage Reward' in t and 'Next Stage' not in t:
            time.sleep(2)
            if 'Next Stage' in flow.joined(flow.ocr(T.grab())): continue  # countdown just slow to render
            c = int(st.group(1))
            log(a, f'{c}-40 cleared, auto stopped -> chapter {c + 1}')
            if 'x2' in step(a, '540,1880', r'Next chapter|x2'):
                log(a, 'game already started the next chapter' + (' -> STOPPED watching (auto runs on: stop it by hand)' if '--stop-next-chapter' in args else ''))
                if '--stop-next-chapter' in args: stopped.add(a)
                continue
            b = flow.ocr(T.grab()); t = flow.joined(b)
        mc = re.search(r'Stage (\d+)-40\b', t)  # main screen, reward already closed (by Nick or us)
        if mc and flow.find(b, r'Next chapter'):
            c = int(mc.group(1))
            step(a, '992,970', rf'Stage ({c + 1}|1)-1\b', 30)   # after 10-40 the next difficulty starts at 1-1 (Kratos Destruction -> Chaos 2026-11-13)
            if '--stop-next-chapter' in args: log(a, f'STOPPED at {c + 1}-1 (main screen, not started)'); stopped.add(a); continue
            time.sleep(1)
            step(a, '994,964', r'^Start$|\| Start \|')
            step(a, '540,1806', FIGHT, 30)
            log(a, f'started {c + 1}-1 on auto')
    if stopped == set(devs): print('all stopped:', sorted(stopped)); sys.exit(0)
    time.sleep(1.5)
print('stopped:', sorted(stopped), 'still climbing:', {a: s[0] for a, s in seen.items() if a not in stopped})
