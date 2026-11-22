#!/usr/bin/env python3
"""Why the Start button didn't show (boot.sh game(), after a launch try) -> one line:
  adb-lost (<adb get-state>)   the ADB link dropped (Chloe, Boudior 2026-11-22: 'device not found' through 10 relaunches)
  not-in-front (<focus>)       game not the focused app (Android home, crashed)
  logged-out (<screen text>)   a login screen, no Start (Kong 2026-11-22) -> boot skips the account, never logs in (CLAUDE.md)
  other (<screen text>)        loading / unknown
usage: D=<serial> scripts/boot_state.py      scripts/boot_state.py --test (offline check of the screen rule)"""
import os, re, subprocess, sys

# Start screen (logged in, 11-22 Bino): 'Support | MINI | HEROES | Account | Community | Repair Client | Start' -> 'Account'
# is on it, so it can't count. The logged-out screen hasn't been read yet: these are the usual login words (untested.md).
LOGIN = r'(?i)\b(log ?in|sign ?in|register|forgot|guest|password)\b'


def screen_state(text):
    if re.search(r'(^| \| )Start( \| |$)', text) or 'Sign Out' in text: return 'other'   # Start shows / own account panel
    return 'logged-out' if re.search(LOGIN, text) else 'other'


def main():
    D = os.environ['D']
    g = subprocess.run(['adb', '-s', D, 'get-state'], capture_output=True, text=True)
    if g.stdout.strip() != 'device': return f'adb-lost ({(g.stdout + g.stderr).strip()[:60]})'
    f = subprocess.run(['adb', '-s', D, 'shell', 'dumpsys', 'window'], capture_output=True, text=True).stdout
    foc = next((l.strip() for l in f.splitlines() if 'mCurrentFocus' in l), '?')
    if 'AppActivity' not in foc: return f'not-in-front ({foc[-50:]})'
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from flow import joined, ocr
    t = joined(ocr())
    return f'{screen_state(t)} ({t[:100]})'


if __name__ == '__main__':
    if sys.argv[1:] == ['--test']:
        assert screen_state('Support | MINI | HEROES | Account | Community | Repair Client | Start') == 'other'
        assert screen_state('Account | G78006234 | Password | Account Binding | Gift | Delete Account | Sign Out | X') == 'other'
        assert screen_state('MINI | HEROES | Log In | Password | Forgot password?') == 'logged-out'
        assert screen_state('Loading... 45%') == 'other'
        print('boot_state --test ok'); sys.exit(0)
    print(main())
