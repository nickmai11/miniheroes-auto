#!/usr/bin/env python3
# Self-check for scripts/accounts.py on a temp accounts dir: all, groups, -drops, unlisted task, typo.
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import accounts

d = accounts.A = tempfile.mkdtemp()
for n in ('a', 'b', 'c', '_template'): open(f'{d}/{n}.yaml', 'w').write('account:\n  mumu_instance: X\n')
open(f'{d}/groups.yaml', 'w').write('g1: [a, b]\n')
open(f'{d}/tasks.yaml', 'w').write('t1: [all, -b]\nt2: [g1, c, -g1]\nt3: [c, a]\nbad: [zz]\n')
assert accounts.for_task('t1') == ['a', 'c']
assert accounts.for_task('t2') == ['c']
assert accounts.for_task('t3') == ['c', 'a']
assert accounts.for_task('unlisted') == ['a', 'b', 'c']
try: accounts.for_task('bad'); assert False
except SystemExit as e: assert 'zz' in str(e)
print('ok')
