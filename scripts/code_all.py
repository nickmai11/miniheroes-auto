#!/usr/bin/env python3
# Gift code on many accounts (skill `code`, Nick 2026-11-13).
# usage: scripts/code_all.py CODE [acct...]   (no accounts = scripts/accounts.py code)  batches of 6: boot (boot.sh) the stopped ones, redeem on each, close only those it booted.
# Instances already running (Kratos: game's own auto stage) are not rebooted - redeemed as they are.
import json, re, subprocess, sys, time, os, concurrent.futures as cf
R = '/Users/nickm/projects/chidojiro/miniheroes-auto'; M = '/Applications/MuMuPlayer Pro.app/Contents/MacOS/mumu-cli'
code, accts = sys.argv[1], sys.argv[2:] or subprocess.check_output([f'{R}/scripts/accounts.py', 'code'], text=True).split()
day = subprocess.check_output(['bash', '-c', 'TZ=UTC date -v-5H +%F'], text=True).strip()
out = f'/tmp/miniheroes-gift-{code}'; os.makedirs(out, exist_ok=True)
def info(): return {r['name'].lower(): r for r in json.loads(subprocess.check_output([M, 'info', 'all']))['return']['results']}
inst = {a: re.search(r'mumu_instance:\s*(\S+)', open(f'{R}/accounts/{a}.yaml').read())[1].lower() for a in accts}
was_up = {a for a in accts if info()[inst[a]].get('state') != 'stopped'}
def log(a, msg):
    print(f'{a}: {msg}', flush=True)
    open(f'{R}/logs/{a}/{day}.log', 'a').write(f'{time.strftime("%F %T")} [claude] giftcode {code} -> {msg}\n')
def redeem(a, serial):
    subprocess.run(['adb', 'connect', serial], capture_output=True)
    p = subprocess.run(['python3', '-W', 'ignore', f'{R}/scripts/giftcode.py', code], cwd=out, env={**os.environ, 'D': serial}, capture_output=True, text=True)
    lines = (p.stdout + p.stderr).strip().splitlines()
    log(a, f'exit {p.returncode}: {lines[-1] if lines else ""}')
for k in range(0, len(accts), 6):
    batch = accts[k:k + 6]; ready = {}
    boot = [a for a in batch if a not in was_up]
    if boot:
        txt = subprocess.run([f'{R}/scripts/boot.sh'] + [str(info()[inst[a]]['index']) for a in boot], capture_output=True, text=True).stdout
        for a in boot:
            m = re.search(rf'^{re.escape(info()[inst[a]]["name"])} (\S+) (.*)$', txt, re.M | re.I)
            if m and m[2].startswith('ready'): ready[a] = m[1]
            else: log(a, f'NOT RUN, boot: {m[0] if m else "no line"}')
    for a in batch:
        if a in was_up: ready[a] = f'127.0.0.1:{info()[inst[a]]["adb_port"]}'
    with cf.ThreadPoolExecutor(6) as ex: list(ex.map(lambda a: redeem(a, ready[a]), list(ready)))
    for a in boot: subprocess.run([M, 'close', str(info()[inst[a]]['index'])], capture_output=True)
