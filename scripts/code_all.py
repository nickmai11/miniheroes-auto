#!/usr/bin/env python3
# Gift code on many accounts (skill `code`, Nick 2026-11-13).
# usage: scripts/code_all.py CODE [acct...]   (no accounts = scripts/accounts.py code)  batches of 6: boot (boot.sh) the stopped ones, redeem on each, close only those it booted.
# Instances already running (Kratos: game's own auto stage) are not rebooted - redeemed as they are.
import json, re, subprocess, sys, time, os, concurrent.futures as cf
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, f'{R}/scripts'); import accounts
M = accounts.MUMU
code, accts = sys.argv[1], sys.argv[2:] or subprocess.check_output([f'{R}/scripts/accounts.py', 'code'], text=True).split()
day = str(accounts.game_day())
out = f'/tmp/miniheroes-gift-{code}'; os.makedirs(out, exist_ok=True)
def info(): return {r['name'].lower(): r for r in json.loads(subprocess.check_output([M, 'info', 'all']))['return']['results']}
inst = {a: accounts.instance(a).lower() for a in accts}
was_up = {a for a in accts if info()[inst[a]].get('state') != 'stopped'}
def log(a, msg):
    print(f'{a}: {msg}', flush=True)
    open(f'{R}/logs/{a}/{day}.log', 'a').write(f'{time.strftime("%F %T")} [claude] giftcode {code} -> {msg}\n')
OK = r'Congratulations|already|has been used|been redeemed'   # reward popup, or the toast "This code has been used" (Cmajor 11-13)   # reward popup or "already redeemed" = done for this account
def redeem(a, serial):
    """Until it's redeemed (Nick 2026-11-13: try until it does): up to 4 tries, a boot.sh restart of the game between tries."""
    for t in range(4):
        subprocess.run(['adb', 'connect', serial], capture_output=True)
        p = subprocess.run(['python3', '-W', 'ignore', f'{R}/scripts/giftcode.py', code], cwd=out, env={**os.environ, 'D': serial}, capture_output=True, text=True)
        txt = re.sub(r"waited \S+ for '[^']*'", '', (p.stdout + p.stderr).strip())   # not the regex echoed in a Stop message
        m = re.search(OK + r'|[Ii]nvalid|expired', txt)
        if m and re.match(OK, m[0]):
            log(a, f'redeemed ({m[0]})')
            if list(inst.values()).count(inst[a]) == 1: subprocess.run([f'{R}/scripts/done.sh', serial])   # done indicator, this account now (CLAUDE.md); Kong + Kong II: neither
            return
        if m: return log(a, f'NOT redeemed: game says {m[0]!r}')
        log(a, f'try {t + 1} failed: {txt.splitlines()[-1][:120] if txt else p.returncode} -> restarting the game')
        bl = subprocess.run([f'{R}/scripts/boot.sh', str(info()[inst[a]]['index'])], capture_output=True, text=True).stdout
        serial = (re.search(r' (127\.0\.0\.1:\d+) ready', bl) or [None, serial])[1]
    log(a, 'NOT redeemed after 4 tries')
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
