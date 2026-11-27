#!/usr/bin/env python3
"""Log a game account in on a fresh instance (Nick 2026-11-27: instance reset) - title screen's "Account Login" ->
Account + Password -> Sign In. Login and password come from the ACCOUNTS list of miniheroes-web.mjs by its `name`
(never printed, never Guest). Stops after Sign In and prints the screen: what follows is checked by the caller.
usage: D=<serial> scripts/login.py <name in miniheroes-web.mjs>"""
import os, re, subprocess, sys, time
from flow import Stop, find, ocr, tap_wait, wait

MJS = os.path.expanduser('~/.local/share/miniheroes/miniheroes-web.mjs')


def creds(name):
    m = re.search(r"name: '%s',[^}]*login: '([^']+)', password: '([^']+)'" % re.escape(name), open(MJS).read())
    if not m: raise Stop(f'no login + password for {name!r} in {MJS}')
    return m[1], m[2]


def type_in(field, s):
    tap_wait(*field); time.sleep(0.8)
    subprocess.run(['adb', '-s', os.environ['D'], 'shell', 'input', 'text', s], check=True); time.sleep(0.5)


if __name__ == '__main__':
    login, password = creds(sys.argv[1])
    b = ocr()
    if not find(b, r'^Password$'):                                  # the first dialog: Google / Email / Account Login
        a = [x for x in b if x[4].strip() == 'Account Login' and x[1] > 900]   # the button, not the dialog's title
        if not a: raise Stop(f'no Account Login button: {" | ".join(x[4] for x in b)[:200]}')
        tap_wait(a[0][0] + a[0][2] // 2, a[0][1] + a[0][3] // 2); wait(r'^Password$', 8)
    type_in((480, 780), login); type_in((480, 896), password)
    tap_wait(540, 1014); time.sleep(3)
    print(f'{sys.argv[1]}: signed in as {login}; screen: ' + ' | '.join(x[4] for x in ocr())[:300])
