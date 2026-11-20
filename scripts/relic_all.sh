#!/bin/bash
# "relics all" with no LLM: relic.py on every accounts/tasks.yaml `relic` instance that is running, in parallel, one result line
# per account (Nick, 2026-11-03). Boot/stabilize first (scripts/boot.sh); an instance with no ADB port is SKIPPED.
# usage: scripts/relic_all.sh [account ...]      (default: accounts/tasks.yaml `relic`)   output + v_relic.png -> /tmp/miniheroes-relic/<account>
# exit 1 lines ("<account> exit 1 (...)") = stopped early: read /tmp/miniheroes-relic/<account>/{out.txt,v_relic.png}
# and finish that account by hand (helper) — never re-run the script blindly on it.
HERE="$(cd "$(dirname "$0")" && pwd)"; R="$(dirname "$HERE")"; W=/tmp/miniheroes-relic
echo "=== $(date)"
pairs=$("$HERE/accounts.py" rows relic "$@")   # "<index>|<account>|<instance>|<port>"; default: accounts/tasks.yaml relic
while IFS='|' read -r _ a _ p; do
  [ -n "$p" ] || { echo "$a SKIPPED (instance not running)"; continue; }
  mkdir -p "$W/$a"
  (cd "$W/$a" && D=127.0.0.1:$p python3 "$HERE/relic.py" "$a" > out.txt 2>&1
   echo "$a exit $? ($(grep -m1 '^done:' out.txt || tail -1 out.txt))") &
done <<<"$pairs"
wait
echo "=== done $(date)"
