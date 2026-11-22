#!/bin/bash
# "catch-up all" with no LLM (Nick, 2026-11-03: scheduled): boot every accounts/tasks.yaml `catchup` instance, daily.py --catch-up on
# each "ready" one in parallel, one result line per account. Leftovers (LEFT FOR HELPER / FAIL) are for Nick or a
# helper later: scripts/summary.sh /tmp/miniheroes-catchup. Output -> logs/launchd-catchup.log when run by launchd.
# --close: close every instance it booted at the end, leftovers too (Nick 2026-11-21, scheduled night run; logs keep them).
HERE="$(cd "$(dirname "$0")" && pwd)"; R="$(dirname "$HERE")"; W=/tmp/miniheroes-catchup
M=$("$HERE/accounts.py" mumu)   # mumu-cli path: one copy, accounts.py
echo "=== $(date)"
pairs=$("$HERE/accounts.py" rows catchup)   # "<index>|<account>|<instance>|<port>"
boot=$("$HERE/boot.sh" $(cut -d'|' -f1 <<<"$pairs"))   # boot.sh does the halves (CPU)
echo "$boot"
# Kong II (S288, on Kong's instance) right after Kong, relics included, then back to Kong (Nick 2026-11-17; CLAUDE.md
# "Kong II"; 2026-11-22: not after every account); stabilize.py exit 0 = that account's ID on screen
kong_ii() {
  OUT="$W/kong_ii" python3 "$HERE/daily.py" kong_ii --catch-up > "$W/kong_ii.log" 2>&1
  echo "kong_ii exit $? ($(grep -m1 'LEFT FOR HELPER' "$W/kong_ii.log" || tail -1 "$W/kong_ii.log"))"
}
. "$HERE/kong_ii.sh"
while IFS='|' read -r i a name _; do
  line=$(grep "^$name 127\.0\.0\.1:" <<<"$boot")
  case $line in *" ready "*) ;; *) echo "$a SKIPPED (${line:-no boot line})"; continue;; esac
  mkdir -p "$W/$a"
  (export D=$(grep -o '127\.0\.0\.1:[0-9]*' <<<"$line"); OUT="$W/$a" python3 "$HERE/daily.py" "$a" --catch-up > "$W/$a.log" 2>&1
   e=$?; echo "$a exit $e ($(grep -m1 'LEFT FOR HELPER' "$W/$a.log" || tail -1 "$W/$a.log"))"
   if [ "$a" = kong ]; then   # done indicator: Kong's instance after Kong II, both clean
     # stale kong_ii.log of an earlier run read as "clean" when the switch failed -> done.sh on a skipped Kong II (11-22)
     mkdir -p "$W/kong_ii"; rm -f "$W/kong_ii.log"; cd "$W/kong_ii" && with_kong_ii kong_ii
     grep -qx 'LEFT FOR HELPER: ' "$W/kong.log" && grep -qx 'LEFT FOR HELPER: ' "$W/kong_ii.log" && "$HERE/done.sh" "$D"
   else [ $e = 0 ] && grep -qx 'LEFT FOR HELPER: ' "$W/$a.log" && "$HERE/done.sh" "$D"; fi) &
done <<<"$pairs"
wait
[ "$1" = --close ] && "$M" close "$(cut -d'|' -f1 <<<"$pairs" | paste -sd, -)" >/dev/null && echo "closed instances $(cut -d'|' -f1 <<<"$pairs" | paste -sd, -)"
"$M" config all --setting '{"maxFpsLimit":60}' >/dev/null && echo "fps back to 60"   # boot.sh set 30 (Nick 2026-11-13)
echo "=== done $(date)"
