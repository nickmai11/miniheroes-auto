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
boot=$(NOLAYOUT=1 "$HERE/boot.sh" $(cut -d'|' -f1 <<<"$pairs"))   # boot.sh does the halves (CPU)
echo "$boot"
while IFS='|' read -r i a name; do
  line=$(grep "^$name 127\.0\.0\.1:" <<<"$boot")
  case $line in *" ready "*) ;; *) echo "$a SKIPPED (${line:-no boot line})"; continue;; esac
  mkdir -p "$W/$a"
  (D=$(grep -o '127\.0\.0\.1:[0-9]*' <<<"$line") OUT="$W/$a" python3 "$HERE/daily.py" "$a" --catch-up > "$W/$a.log" 2>&1
   echo "$a exit $? ($(grep -m1 'LEFT FOR HELPER' "$W/$a.log" || tail -1 "$W/$a.log"))") &
done <<<"$pairs"
wait
# relics last, on every catch-up account - never filtered by the relic list (Nick 2026-11-10 / 2026-11-16)
"$HERE/relic_all.sh" $("$HERE/accounts.py" catchup)
# Kong II (S288, on Kong's instance) once Kong is done, relics included, then back to Kong (Nick 2026-11-17; CLAUDE.md
# "Kong II"); stabilize.py exit 0 = that account's ID on screen
export D=$(grep '^Kong 127\.0\.0\.1:.* ready ' <<<"$boot" | grep -o '127\.0\.0\.1:[0-9]*')
if grep -q '|kong|' <<<"$pairs" && [ -n "$D" ]; then
  mkdir -p "$W/kong_ii"; cd "$W/kong_ii"
  if ACCOUNT=kong_ii python3 "$HERE/stabilize.py" > switch.txt 2>&1; then
    OUT="$W/kong_ii" python3 "$HERE/daily.py" kong_ii --catch-up > "$W/kong_ii.log" 2>&1
    echo "kong_ii exit $? ($(grep -m1 'LEFT FOR HELPER' "$W/kong_ii.log" || tail -1 "$W/kong_ii.log"))"
    python3 "$HERE/relic.py" kong_ii > out.txt 2>&1; echo "kong_ii relic exit $? ($(grep -m1 '^done:' out.txt || tail -1 out.txt))"
  else echo "kong_ii SKIPPED (switch: $(tail -1 switch.txt))"; fi
  ACCOUNT=kong python3 "$HERE/stabilize.py" >> switch.txt 2>&1 || echo "kong: switch back from Kong II failed ($(tail -1 switch.txt))"
fi
"/Applications/MuMuPlayer Pro.app/Contents/MacOS/mumu-cli" config all --setting '{"maxFpsLimit":60}' >/dev/null && echo "fps back to 60"   # boot.sh set 30 (Nick 2026-11-13)
echo "=== done $(date)"
