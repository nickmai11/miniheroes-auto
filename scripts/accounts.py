#!/usr/bin/env python3
# Accounts a task runs on (Nick, 2026-11-06): accounts/tasks.yaml `<task>: [...]`, items = account, group
# (accounts/groups.yaml), `all`, or `-<account|group>` to drop, left to right. Task not listed -> all accounts.
# usage: scripts/accounts.py <task>   -> one account name per line (exit 1 on an unknown name = typo in the yaml)
import glob, os, re, sys
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'accounts')


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
    print('\n'.join(for_task(sys.argv[1])))
