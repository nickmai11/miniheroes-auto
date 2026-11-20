#!/usr/bin/env python3
# Rename an account everywhere (Nick 2026-11-20, xfaktor -> pawn1): accounts/<old>.yaml -> <new>.yaml (name +
# mumu_instance), the old key / display name / instance name in every repo file (not docs/archive, not the in-game
# name lists own_accounts.txt / tribe_*.txt: those hold in-game names, see the rename-account skill), the MuMu instance
# (vmName in its bundle's setting/vm.json, instance must be stopped), logs/<old> and /tmp/miniheroes-state/<old>-*.
# usage: scripts/rename_account.py <old key> <new key> [--name <display = instance name>] [--dry]
import glob, json, os, re, subprocess, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = '/Applications/MuMuPlayer Pro.app/Contents/MacOS/mumu-cli'
SKIP = ('docs/archive/', 'accounts/own_accounts.txt', 'accounts/tribe_')


def sub(text, pairs):
    """Whole-word, case-sensitive replace of each (old, new) pair."""
    for old, new in pairs:
        text = re.sub(r'\b' + re.escape(old) + r'\b', new, text)
    return text


def main():
    a = [x for x in sys.argv[1:] if x != '--dry']
    dry = '--dry' in sys.argv
    old, new = a[0], a[1]
    name = a[a.index('--name') + 1] if '--name' in a else new
    if ' ' in name: sys.exit('no spaces in the instance name (scripts read it with \\S+)')
    f_old, f_new = f'{R}/accounts/{old}.yaml', f'{R}/accounts/{new}.yaml'
    cfg = open(f_old).read()
    old_name = re.search(r'^\s*name:\s*(\S+)', cfg, re.M)[1]
    old_inst = re.search(r'^\s*mumu_instance:\s*(\S+)', cfg, re.M)[1]
    pairs = sorted({(old, new), (old_name, name), (old_inst, name)} - {(name, name)}, key=lambda p: -len(p[0]))

    files = subprocess.check_output(['git', '-C', R, 'ls-files'], text=True).split()
    for rel in files:
        if rel.startswith(SKIP) or not rel.endswith(('.md', '.yaml', '.py', '.sh', '.txt', '.js')): continue
        p = f'{R}/{rel}'
        t = open(p).read()
        n = sub(t, pairs)
        if n != t:
            print('edit', rel)
            if not dry: open(p, 'w').write(n)
    print('git mv', f_old, '->', f_new)
    if not dry: subprocess.check_call(['git', '-C', R, 'mv', f_old, f_new])

    for r in json.loads(subprocess.check_output([CLI, 'info', 'all']))['return']['results']:
        if r['name'] != old_inst: continue
        if r.get('state') != 'stopped': sys.exit(f'instance {old_inst} is {r.get("state")}: stop it, then re-run')
        vm = f'{r["bundle_path"]}/setting/vm.json'
        print('MuMu vmName', old_inst, '->', name, vm)
        if not dry:
            v = json.load(open(vm)); v['vmName'] = name; json.dump(v, open(vm, 'w'), indent=4)

    moves = [(f'{R}/logs/{old}', f'{R}/logs/{new}')] if os.path.isdir(f'{R}/logs/{old}') else []
    moves += [(s, s.replace(f'/{old}-', f'/{new}-', 1)) for s in glob.glob(f'/tmp/miniheroes-state/{old}-*')]
    for s, d in moves:
        print('mv', s, '->', d)
        if not dry: os.rename(s, d)

    left = subprocess.run(['git', '-C', R, 'grep', '-il', old, '--', '.', ':!docs/archive'], capture_output=True, text=True).stdout
    if left: print('still mention', old, '(other casing / in-game lists - check by hand):\n' + left)


if __name__ == '__main__':
    assert sub('xFaktor, xfaktor.yaml; xfaktors', [('xfaktor', 'pawn1'), ('xFaktor', 'pawn1')]) == 'pawn1, pawn1.yaml; xfaktors'
    main()
