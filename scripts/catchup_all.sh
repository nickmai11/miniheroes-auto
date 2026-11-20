#!/bin/bash
# "catch-up all" with no LLM (Nick, 2026-11-03: scheduled): boot every accounts/tasks.yaml `catchup` instance, daily.py --catch-up on
# each "ready" one in parallel, one result line per account. Leftovers (LEFT FOR HELPER / FAIL) are for Nick or a
# helper later: scripts/summary.sh /tmp/miniheroes-catchup. Output -> logs/launchd-catchup.log when run by launchd.
HERE="$(cd "$(dirname "$0")" && pwd)"; R="$(dirname "$HERE")"; W=/tmp/miniheroes-catchup
M=$("$HERE/accounts.py" mumu)   # mumu-cli path: one copy, accounts.py
echo "=== $(date)"
pairs=$("$HERE/accounts.py" rows catchup)   # "<index>|<account>|<instance>|<port>"
boot=$("$HERE/boot.sh" $(cut -d'|' -f1 <<<"$pairs"))   # boot.sh does the halves (CPU)
echo "$boot"
while IFS='|' read -r i a name _; do
  line=$(grep "^$name 127\.0\.0\.1:" <<<"$boot")
  case $line in *" ready "*) ;; *) echo "$a SKIPPED (${line:-no boot line})"; continue;; esac
  mkdir -p "$W/$a"
  (export D=$(grep -o '127\.0\.0\.1:[0-9]*' <<<"$line"); OUT="$W/$a" python3 "$HERE/daily.py" "$a" --catch-up > "$W/$a.log" 2>&1
   e=$?; echo "$a exit $e ($(grep -m1 'LEFT FOR HELPER' "$W/$a.log" || tail -1 "$W/$a.log"))"
   # done indicator: clean accounts only; Kong's instance after Kong II (below)
   [ $e = 0 ] && [ "$a" != kong ] && grep -qx 'LEFT FOR HELPER: ' "$W/$a.log" && "$HERE/done.sh" "$D") &
done <<<"$pairs"
wait
# Kong II (S288, on Kong's instance) once Kong is done, relics included, then back to Kong (Nick 2026-11-17; CLAUDE.md
# "Kong II"); stabilize.py exit 0 = that account's ID on screen
export D=$(grep '^Kong 127\.0\.0\.1:.* ready ' <<<"$boot" | grep -o '127\.0\.0\.1:[0-9]*')
if grep -q '|kong|' <<<"$pairs" && [ -n "$D" ]; then
  mkdir -p "$W/kong_ii"; cd "$W/kong_ii"
  kong_ii() {
    OUT="$W/kong_ii" python3 "$HERE/daily.py" kong_ii --catch-up > "$W/kong_ii.log" 2>&1
    echo "kong_ii exit $? ($(grep -m1 'LEFT FOR HELPER' "$W/kong_ii.log" || tail -1 "$W/kong_ii.log"))"
  }
  . "$HERE/kong_ii.sh"; with_kong_ii kong_ii
  grep -qx 'LEFT FOR HELPER: ' "$W/kong.log" && grep -qx 'LEFT FOR HELPER: ' "$W/kong_ii.log" && "$HERE/done.sh" "$D"
fi
"$M" config all --setting '{"maxFpsLimit":60}' >/dev/null && echo "fps back to 60"   # boot.sh set 30 (Nick 2026-11-13)
echo "=== done $(date)"
