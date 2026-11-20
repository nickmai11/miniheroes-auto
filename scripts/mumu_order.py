#!/usr/bin/env python3
# MuMuPlayer launcher list order = accounts/layout.yaml `mumu:` (Nick 2026-11-13).
# MuMu keeps it in setting/common.json "managerListIndexs" = "<instance index>-<list position>,..." (backup 10-26:
# "15-13,16-14" = instances 15/16 shown 14th/15th). No mumu-cli command for it. The launcher reads the file at start,
# so it shows the new order after its next launch; unlisted instances go after the listed ones, by index.
# usage: scripts/mumu_order.py [--dry]
import json, os, re, shutil, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.expanduser('~/Library/Application Support/com.netease.mumu.nemux-global/setting/common.json')
from accounts import MUMU as CLI

def build(order, idx):
    """order: names; idx: {name: index} -> 'i-pos,...' (positions follow `order`, then the rest by index)."""
    low = {n.lower(): i for n, i in idx.items()}
    miss = [n for n in order if n.lower() not in low]
    if miss: raise SystemExit(f'not a MuMu instance: {miss}')
    seq = [low[n.lower()] for n in order]
    seq += sorted(i for i in idx.values() if i not in seq)
    return ','.join(f'{i}-{p}' for p, i in enumerate(seq))

if __name__ == '__main__':
    assert build(['B', 'a'], {'a': 0, 'B': 1, 'c': 2}) == '1-0,0-1,2-2'
    order = [s.strip() for s in re.search(r'^mumu:\s*\[([^\]]*)\]', open(f'{HERE}/../accounts/layout.yaml').read(), re.M)[1].split(',')]
    idx = {r['name']: int(r['index']) for r in json.loads(subprocess.check_output([CLI, 'info', 'all']))['return']['results']}
    val = build(order, idx)
    print(val)
    if '--dry' in sys.argv: sys.exit()
    shutil.copy(F, f'{F}.bak-{time.strftime("%Y%m%d%H%M%S")}')
    d = json.load(open(F)); d['managerListIndexs'] = val
    json.dump(d, open(F, 'w'), indent=2)
    print(f'written to {F}; shows after the MuMuPlayer launcher restarts')
