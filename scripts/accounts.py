#!/usr/bin/env python3
# Accounts a task runs on (Nick, 2026-11-06): accounts/tasks.yaml `<task>: [...]`, items = account, group
# (accounts/groups.yaml), `all`, or `-<account|group>` to drop, left to right. Task not listed -> all accounts.
# usage: scripts/accounts.py <task>   -> one account name per line (exit 1 on an unknown name = typo in the yaml)
#        scripts/accounts.py rows <task> [account ...]   -> "<mumu index>|<account>|<instance>|<adb port or empty>" per
#        account (the given ones, else the task's) whose instance exists - the one account -> instance lookup (Nick 2026-11-20)
#        scripts/accounts.py boot-order <mumu index>...   -> the indices in boot order (boot.sh)
#        scripts/accounts.py mumu | game-day   -> the mumu-cli path / today's game day (for the shell scripts and layout.js)
import datetime, glob, json, os, re, subprocess, sys
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'accounts')
MUMU = '/Applications/MuMuPlayer Pro.app/Contents/MacOS/mumu-cli'   # the one copy


def game_day():
    """Game day as a date: resets 05:00 UTC - names logs/<account>/<day>.log. The one copy."""
    return (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=5)).date()


def field(acct, key):
    """`key:` value in accounts/<acct>.yaml (inline comment stripped), else None."""
    f = f'{A}/{acct}.yaml'
    m = os.path.exists(f) and re.search(rf'^\s*{key}:\s*([^#\n]*?)\s*(#|$)', open(f).read(), re.M)
    return m[1] if m and m[1] not in ('', 'null') else None


def instance(acct):
    """MuMu instance name: mumu_instance, or `instance` for an account sharing one (Kong II on Kong's)."""
    return field(acct, 'mumu_instance') or field(acct, 'instance')


def of_instance(name):
    """The account whose own instance (mumu_instance) is `name`, else None."""
    return next((a for a in every() if field(a, 'mumu_instance') == name), None)


def mumu():
    """{instance name: mumu-cli info row (index, adb_port when running, ...)}"""
    return {r['name']: r for r in json.loads(subprocess.check_output([MUMU, 'info', 'all']))['return']['results']}


def rows(accts):
    info = mumu()
    return [(info[i]['index'], a, i, info[i].get('adb_port') or '') for a in accts if (i := instance(a)) in info]


def boot_order(idx):
    """MuMu indices in layout-1 screen order, right to left then top to bottom (Nick 2026-11-22): `right` column, `top`
    row, `bottom` row of accounts/layout.yaml; instances not in the layout last, as given."""
    L = lists(f'{A}/layout.yaml')
    slots = L.get('right', [])[::-1] + L.get('top', [])[::-1] + L.get('bottom', [])[::-1]
    name = {str(r['index']): n for n, r in mumu().items()}
    return sorted(idx, key=lambda i: slots.index(name[i]) if name.get(i) in slots else len(slots))


def lists(f):
    return {k: [x.strip() for x in v.split(',') if x.strip()] for k, v in re.findall(r'^(\w+):\s*\[(.*?)\]', open(f).read(), re.M)}


def every():
    """Account names = accounts/*.yaml with a mumu_instance (not the template, groups, layout or tasks files)."""
    return sorted(os.path.basename(f)[:-5] for f in glob.glob(f'{A}/*.yaml')
                  if not os.path.basename(f).startswith('_') and re.search(r'^\s*mumu_instance:', open(f).read(), re.M))


def for_task(task):
    allx, groups, out = every(), lists(f'{A}/groups.yaml'), []
    for x in lists(f'{A}/tasks.yaml').get(task, ['all']):
        drop, x = x.startswith('-'), x.lstrip('-')
        for n in allx if x == 'all' else groups.get(x, [x]):
            if n not in allx: sys.exit(f'accounts/tasks.yaml {task}: unknown account {n!r}')
            if drop: out = [o for o in out if o != n]
            elif n not in out: out.append(n)
    return out


if __name__ == '__main__':
    if sys.argv[1] == 'mumu': print(MUMU)
    elif sys.argv[1] == 'game-day': print(game_day())
    elif sys.argv[1] == 'boot-order': print(' '.join(boot_order(sys.argv[2:])))
    elif sys.argv[1] == 'rows': print('\n'.join('|'.join(map(str, r)) for r in rows(sys.argv[3:] or for_task(sys.argv[2]))))
    else: print('\n'.join(for_task(sys.argv[1])))
