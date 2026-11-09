#!/bin/bash
# "catch-up all" with no LLM (Nick, 2026-11-03: scheduled): boot every accounts/tasks.yaml `catchup` instance, daily.py --catch-up on
# each "ready" one in parallel, one result line per account. Leftovers (LEFT FOR HELPER / FAIL) are for Nick or a
# helper later: scripts/summary.sh /tmp/miniheroes-catchup. Output -> logs/launchd-catchup.log when run by launchd.
HERE="$(cd "$(dirname "$0")" && pwd)"; R="$(dirname "$HERE")"; W=/tmp/miniheroes-catchup
echo "=== $(date)"
pairs=$(python3 - "$R" <<'PY'
import glob, json, re, subprocess, sys
sys.path.insert(0, sys.argv[1] + '/scripts'); from accounts import for_task
want = for_task('catchup')   # accounts/tasks.yaml
info = json.loads(subprocess.check_output(['/Applications/MuMuPlayer Pro.app/Contents/MacOS/mumu-cli', 'info', 'all']))
idx = {r['name']: r['index'] for r in info['return']['results']}
for f in sorted(glob.glob(sys.argv[1] + '/accounts/*.yaml')):
    m = re.search(r'mumu_instance:\s*(.+)', open(f).read())
    if m and m[1].strip() in idx and f.rsplit('/', 1)[1][:-5] in want: print(f"{idx[m[1].strip()]}|{f.rsplit('/', 1)[1][:-5]}|{m[1].strip()}")
PY
)
boot=$(for i in $(cut -d'|' -f1 <<<"$pairs"); do "$HERE/boot.sh" "$i" & done; wait)
echo "$boot"
while IFS='|' read -r i a name; do
  line=$(grep "^$name 127\.0\.0\.1:" <<<"$boot")
  case $line in *" ready "*) ;; *) echo "$a SKIPPED (${line:-no boot line})"; continue;; esac
  mkdir -p "$W/$a"
  (D=$(grep -o '127\.0\.0\.1:[0-9]*' <<<"$line") OUT="$W/$a" python3 "$HERE/daily.py" "$a" --catch-up > "$W/$a.log" 2>&1
   echo "$a exit $? ($(grep -m1 'LEFT FOR HELPER' "$W/$a.log" || tail -1 "$W/$a.log"))") &
done <<<"$pairs"
wait
# relics last (Nick, 2026-11-10): catch-up accounts that are also in accounts/tasks.yaml relic
"$HERE/relic_all.sh" $(comm -12 <("$HERE/accounts.py" catchup | sort) <("$HERE/accounts.py" relic | sort))
echo "=== done $(date)"
