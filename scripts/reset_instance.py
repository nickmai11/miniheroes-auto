#!/usr/bin/env python3
"""Replace an account's MuMu instance by a fresh clone of the base instance (Nick 2026-11-27: "reset mumu instances"):
clone 'Android Device' -> open -> start the game -> Account Login (scripts/login.py, credentials from
miniheroes-web.mjs) -> Start -> the game id at the top right must equal <game id> -> only then the old instance is
deleted and the clone takes its name. Any other outcome = exit 1 with both instances kept (the clone as "<name> new").
usage: scripts/reset_instance.py <instance name> <name in miniheroes-web.mjs> <game id>"""
import json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
M = subprocess.check_output([os.path.join(HERE, 'accounts.py'), 'mumu'], text=True).strip()
BASE = 'Android Device'


def mumu(*a):
    r = json.loads(subprocess.check_output([M, *map(str, a)]))
    if r.get('errcode'): sys.exit(f'mumu-cli {a}: {r}')
    return r['return']


def rows(): return {r['name']: r for r in mumu('info', 'all')['results']}


def up(i):
    """Open instance i and wait until Android has booted; returns its adb serial."""
    mumu('open', i)
    for _ in range(90):
        p = mumu('info', i).get('adb_port')
        if p:
            s = f'127.0.0.1:{p}'; subprocess.run(['adb', 'connect', s], capture_output=True)
            if subprocess.run(['adb', '-s', s, 'shell', 'getprop', 'sys.boot_completed'], capture_output=True, text=True).stdout.strip() == '1': return s
        time.sleep(2)
    sys.exit(f'instance {i}: Android not up after 3 min')


if __name__ == '__main__':
    name, web, want = sys.argv[1:4]
    info = rows()
    if name not in info or BASE not in info or f'{name} new' in info: sys.exit(f'{name}: old / base instance missing, or "{name} new" already there')
    old, t0 = info[name]['index'], time.time()
    new = mumu('clone', info[BASE]['index'])['index']
    mumu('config', new, '--setting', json.dumps({'vmName': f'{name} new'}))
    os.environ['D'] = up(new)
    sys.path.insert(0, HERE)
    import login                                                    # after D: tap.py reads it at import
    from flow import ocr, tap_wait, wait
    for n in range(4):                                              # the game's icon on the Android home; a tap right after boot can do nothing (Aminor, Pawn I)
        time.sleep(3); tap_wait(540, 340)
        try: wait(r'Account Login', 30); break
        except Exception:
            if n == 3: raise
    acct, password = login.creds(web)
    tap_wait(540, 1008); wait(r'^Password$', 8)
    login.type_in((480, 780), acct); login.type_in((480, 896), password)
    tap_wait(540, 1014); b = wait(r'^Start$', 30)                    # a wrong password never shows Start
    tap_wait(540, 1510); wait(r'\d{8}', 150, (600, 0, 1080, 80))    # main screen: "<game id> | p2 | <version>" top right
    got = re.search(r'\d{8}', ' '.join(t for x, y, w, h, t in ocr() if y < 80 and x > 600))
    got = got[0] if got else '?'
    if got != want: sys.exit(f'{name}: game id on screen {got}, expected {want} -> nothing deleted, clone kept as "{name} new" (index {new})')
    mumu('close', new); time.sleep(3)
    mumu('delete', old)
    mumu('config', new, '--setting', json.dumps({'vmName': name}))
    print(f'{name}: id {got} ok, old index {old} deleted, new index {new} ({time.time() - t0:.0f}s)', flush=True)
