#!/bin/bash
# "relics all" with no LLM: relic.py on every accounts/*.yaml instance that is running, in parallel, one result line
# per account (Nick, 2026-11-03). Boot/stabilize first (scripts/boot.sh); an instance with no ADB port is SKIPPED.
# usage: scripts/relic_all.sh [account ...]      (default: every account)   output + v_relic.png -> /tmp/miniheroes-relic/<account>
# exit 1 lines ("<account> exit 1 (...)") = stopped early: read /tmp/miniheroes-relic/<account>/{out.txt,v_relic.png}
# and finish that account by hand (helper) — never re-run the script blindly on it.
HERE="$(cd "$(dirname "$0")" && pwd)"; R="$(dirname "$HERE")"; W=/tmp/miniheroes-relic
echo "=== $(date)"
pairs=$(python3 - "$R" "$@" <<'EOF'
import glob, json, re, subprocess, sys
info = json.loads(subprocess.check_output(['/Applications/MuMuPlayer Pro.app/Contents/MacOS/mumu-cli', 'info', 'all']))
port = {r['name']: r.get('adb_port') for r in info['return']['results']}
only = set(sys.argv[2:])
for f in sorted(glob.glob(sys.argv[1] + '/accounts/*.yaml')):
    a = f.rsplit('/', 1)[1][:-5]
    m = re.search(r'mumu_instance:\s*(.+)', open(f).read())
    if m and m[1].strip() in port and (not only or a in only): print(f"{a}|{port[m[1].strip()] or ''}")
EOF
)
while IFS='|' read -r a p; do
  [ -n "$p" ] || { echo "$a SKIPPED (instance not running)"; continue; }
  mkdir -p "$W/$a"
  (cd "$W/$a" && D=127.0.0.1:$p python3 "$HERE/relic.py" "$a" > out.txt 2>&1
   echo "$a exit $? ($(grep -m1 '^done:' out.txt || tail -1 out.txt))") &
done <<<"$pairs"
wait
echo "=== done $(date)"
