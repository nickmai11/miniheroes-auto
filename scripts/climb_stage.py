#!/usr/bin/env python3
# Babysit the game's own auto stage climb (occasional, not part of the dailies): auto stops after X-40 (3-wave boss)
# -> close the reward, Next chapter, open the stage, Start; Defeat screen up 3 s -> Challenge again.
# usage: scripts/climb_stage.py <account>... [--minutes N]   |   scripts/climb_stage.py <account> --swap | --record | --apply
# --apply: put the yaml stage_lineups back on all 3 tabs (after a SWAP LINEUPS FAILED), then Start.
# --record [--no-start]: from any screen -> fresh battle setup, read each tab's deployed cells (green checks), write
# stage_lineups, then Start (unless --no-start). Grid rows are found by measuring each slow-drag scroll.
# Accounts = accounts/<account>.yaml names; the game is moved to the stage if it's elsewhere.
# Runs N minutes (default 9, fits one Bash call) then exits 0 "still climbing" — just run it again.
# Lost the same stage 3x in a row -> swap the losing wave's team with the next tab (stage_lineups cells in the account
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
ports = {x['name']: x.get('adb_port') for x in json.loads(subprocess.run([M, 'info', 'all'], capture_output=True, text=True).stdout)['return']['results']}
devs = {}
for a in accts:
    inst = re.search(r'mumu_instance:\s*(.+)', open(f'{R}/accounts/{a}.yaml').read()).group(1).strip()
    if not ports.get(inst): sys.exit(f'{a}: instance {inst} not running')
    devs[a] = f'127.0.0.1:{ports[inst]}'
    subprocess.run(['adb', 'connect', devs[a]], capture_output=True)   # drops after the Mac sleeps (2026-11-01)
os.environ['D'] = next(iter(devs.values()))
sys.path.insert(0, HERE)
import flow, tap as T

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
    short drag keeps the true shift the only match in 20-300; a poor best match raises instead of guessing."""
    b = gray(); adb(d, 'swipe', 540, 1450, 540, 1330, 2000); time.sleep(1.2); a = gray()
    err = {s: abs(a[1150:1230] - b[1150 + s:1230 + s]).mean() for s in range(20, 301, 2)}
    s = min(err, key=err.get)
    if err[s] > 12: raise RuntimeError(f'grid scroll not measurable (best {s}px, err {err[s]:.0f})')
    return s


def grid_pass(d, rows_needed, fn):
    """Call fn({row: y}) for the rows visible at each scroll position (each row once), scrolling down as needed."""
    to_top(d); off, done, retries = 0, set(), 0
    for _ in range(10):
        vis = {r: ROW1 + (r - 1) * PITCH - off for r in rows_needed if r not in done and 1180 < ROW1 + (r - 1) * PITCH - off < 1520}
        if vis: fn(vis); done |= set(vis)
        if done >= set(rows_needed): return
        try: off += scroll(d)
        except RuntimeError:   # a slow drag sometimes flings far past 300 px (Chien Than 7-20, 2026-11-02): from the top again
            retries += 1
            if retries > 2: raise
            to_top(d); off = 0
    raise RuntimeError(f'rows {set(rows_needed) - done} never visible')


def swap(a, k=1):
    """Losing wave = the open tab of the Challenge-again setup. Fresh setup from the main screen (Challenge-again
    edits aren't saved), recall both tabs, deploy each other's cells (rows 1-3), re-read the cells, rewrite the yaml, Start.
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
    if any(len(teams[t]) != 5 for t in (w, o)): log(a, f'SWAP LINEUPS: lineups unreadable {teams}, nothing changed'); sys.exit(2)
    for t in (w, o): step(a, f'{TAB[t]},1088', 'Start'); step(a, '1000,1080', 'Start')
    def place(vis):
        for t, cells in ((w, teams[o]), (o, teams[w])):
            step(a, f'{TAB[t]},1088', 'Start')
            for c in cells:
                if int(c[1]) in vis: adb(d, 'tap', COLX[int(c[3]) - 1], vis[int(c[1])]); time.sleep(0.6)
    grid_pass(d, sorted({int(c[1]) for c in teams[o] + teams[w]}), place)
    want = {**teams, w: teams[o], o: teams[w]}
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
    r = subprocess.run(['python3', '-c', 'import daily; print(daily.home())'], cwd=HERE, env={**os.environ, 'D': d}, capture_output=True, text=True)
    if 'True' not in r.stdout: log(a, 'could not reach the main screen'); sys.exit(1)


def apply(a):
    T.D = flow.D = devs[a]; d = devs[a]
    y = open(f'{R}/accounts/{a}.yaml').read()
    teams = {int(k): v.split(', ') for k, v in re.findall(r'^\s+(\d): \{cells: \[([^\]]*)\]', y, re.M)}
    to_main(a)
    step(a, '994,964', r'^Start$|\| Start \|')
    for t in (1, 2, 3): step(a, f'{TAB[t]},1088', 'Start'); step(a, '1000,1080', 'Start')
    def place(vis):
        for t in (1, 2, 3):
            step(a, f'{TAB[t]},1088', 'Start')
            for c in teams[t]:
                if int(c[1]) in vis: adb(d, 'tap', COLX[int(c[3]) - 1], vis[int(c[1])]); time.sleep(0.6)
    grid_pass(d, sorted({int(c[1]) for v in teams.values() for c in v}), place)
    got = read_lineups(a)
    if any(sorted(got[t]) != sorted(teams[t]) for t in (1, 2, 3)):
        log(a, f'APPLY FAILED: tabs read {got}, yaml {teams} - left on setup'); sys.exit(2)
    log(a, f'applied yaml lineups {teams}')
    step(a, '540,1806', FIGHT, 30)


def checked(im, x, y0, y1):
    """Green deploy check on the card at column x between y0..y1."""
    return sum(1 for dx in range(-50, 51, 6) for y in range(y0, y1, 6)
               if (lambda p: p[1] > 170 and p[0] < 160 and p[2] < 120)(im.getpixel((x + dx, y)))) >= 8


def read_lineups(a):
    """On a fresh battle setup: each tab's deployed cells (green checks, rows 1-5)."""
    d = devs[a]
    teams = {1: [], 2: [], 3: []}
    def read(vis):
        for t in (1, 2, 3):
            step(a, f'{TAB[t]},1088', 'Start'); time.sleep(0.6); im = T.grab()
            teams[t] += [f'r{r}c{c + 1}' for r, yc in vis.items() for c, x in enumerate(COLX) if checked(im, x, yc - 75, yc + 75)]
    grid_pass(d, [1, 2, 3, 4, 5], read)
    multi = {c for t in teams for c in teams[t] if sum(c in v for v in teams.values()) > 1}   # green card art (xFaktor r4c2)
    return {t: [c for c in v if c not in multi] for t, v in teams.items()}


def record(a):
    T.D = flow.D = devs[a]
    to_main(a)
    step(a, '994,964', r'^Start$|\| Start \|')
    teams = read_lineups(a)
    bad = [t for t in teams if len(teams[t]) != 5]
    if bad: log(a, f'record: tabs {bad} not 5 cells in rows 1-5: {teams} (heroes further down?) - not written'); sys.exit(1)
    write_lineups(a, teams)
    log(a, f'recorded stage_lineups {teams}')
    if '--no-start' in args: return
    step(a, '540,1806', FIGHT, 30)
    log(a, 'started the stage')


def write_lineups(a, teams):
    path = f'{R}/accounts/{a}.yaml'; y = open(path).read()
    y = re.sub(r'\n  stage_lineups:.*?(?=\n  \S|\Z)', '', y, flags=re.S)
    y = y.rstrip('\n') + '\n  stage_lineups:   # see bino.yaml; recorded by climb_stage.py --record ' + time.strftime('%F') + '\n' + ''.join(
        f'    {t}: {{cells: [{", ".join(teams[t])}], good_for: ""}}\n' for t in (1, 2, 3))
    open(path, 'w').write(y)


def start(a):
    """Not on a stage battle/result/setup (Nick used the account) -> main screen (daily.home) -> skull -> Start."""
    T.D = flow.D = devs[a]
    for _ in range(5):   # between fights the screen can be blank/loading (xFaktor 2026-11-01): look a few times
        t = flow.joined(flow.ocr(T.grab()))
        if re.search(r'Stage: ?\d+-\d+|x2|Victory|Defeat|Challenge|Next Stage|Tap anywhere', t): return
        time.sleep(1.5)
    r = subprocess.run(['python3', '-c', 'import daily; print(daily.home())'], cwd=HERE, env={**os.environ, 'D': devs[a]},
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
seen, losses, swaps = {}, {}, {}
end = time.time() + minutes * 60
while time.time() < end:
    for a, d in devs.items():
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
                    swaps[stage] = swaps.get(stage, 0) + 1
                    if swaps[stage] > 3: log(a, f'SWAP LINEUPS: {stage} still lost after 3 swaps, left on the battle setup'); sys.exit(2)
                    swap(a, swaps[stage]); losses.pop(a); seen.pop(a, None); continue
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
            if 'x2' in step(a, '540,1880', r'Next chapter|x2'): log(a, 'game already started the next chapter'); continue
            b = flow.ocr(T.grab()); t = flow.joined(b)
        mc = re.search(r'Stage (\d+)-40\b', t)  # main screen, reward already closed (by Nick or us)
        if mc and flow.find(b, r'Next chapter'):
            c = int(mc.group(1))
            step(a, '992,970', rf'Stage {c + 1}-1\b', 30)
            time.sleep(1)
            step(a, '994,964', r'^Start$|\| Start \|')
            step(a, '540,1806', FIGHT, 30)
            log(a, f'started {c + 1}-1 on auto')
    time.sleep(1.5)
print('still climbing:', {a: s[0] for a, s in seen.items()})
