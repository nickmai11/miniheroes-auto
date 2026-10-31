#!/usr/bin/env python3
# Babysit the game's own auto stage climb (occasional, not part of the dailies): auto stops after X-40 (3-wave boss)
# -> close the reward, Next chapter, open the stage, Start; Defeat screen up 3 s -> Challenge again.
# usage: scripts/climb.py <account>... [--minutes N]     (accounts/<account>.yaml; game must already be auto-climbing)
# Runs N minutes (default 9, fits one Bash call) then exits 0 "still climbing" — just run it again.
# exit 2 = lost the same stage 3x in a row: swap lineups by hand (accounts/<a>.yaml stage_lineups), re-run.
# exit 1 = a step's screen didn't show or a stage didn't change for 4 min (climb_<name>.png in /tmp).
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
os.environ['D'] = next(iter(devs.values()))
sys.path.insert(0, HERE)
import flow, tap as T

gd = subprocess.run('TZ=UTC date -v-5H +%F', shell=True, capture_output=True, text=True).stdout.strip()


def log(a, msg):
    line = f"{time.strftime('%F %T')} [climb] {msg}"
    print(a, line, flush=True)
    os.makedirs(f'{R}/logs/{a}', exist_ok=True)
    open(f'{R}/logs/{a}/{gd}.log', 'a').write(line + '\n')


def step(a, xy, pat, to=20):
    r = subprocess.run(['python3', f'{HERE}/tap.py', xy, '-o', f'/tmp/climb_{a}.png', '-w', '270', '--until-text', pat,
                        '--timeout', str(to)], env={**os.environ, 'D': devs[a]}, capture_output=True, text=True)
    if r.returncode: log(a, f'FAIL waiting {pat!r} after {xy}: {r.stdout.strip()[-300:]}'); sys.exit(1)
    return r.stdout


FIGHT = r'Victory|Defeat|Lv\.|x2|ATK'  # any of these = a battle (or its result) is on


def start(a):
    """Not on a stage battle/result/setup (Nick used the account) -> main screen (daily.home) -> skull -> Start."""
    T.D = flow.D = devs[a]
    b = flow.ocr(T.grab()); t = flow.joined(b)
    if re.search(r'Stage: ?\d+-\d+', t) or 'x2' in t: return
    r = subprocess.run(['python3', '-c', 'import daily; print(daily.home())'], cwd=HERE, env={**os.environ, 'D': devs[a]},
                       capture_output=True, text=True)
    if 'True' not in r.stdout: log(a, f'FAIL: could not reach the main screen ({r.stdout.strip()} {r.stderr.strip()[-200:]})'); sys.exit(1)
    step(a, '994,964', r'^Start$|\| Start \|')
    step(a, '540,1806', FIGHT, 30)
    log(a, 'was off the stage screen -> main -> started the stage')


for a in devs: start(a)
seen, losses = {}, {}
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
                    log(a, f'SWAP LINEUPS: lost {stage} 3x, left on the battle setup'); sys.exit(2)
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
