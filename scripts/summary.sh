#!/bin/sh
# One compact view of a daily.py run (Nick, 2026-10-29: the coordinator grepped logs ~60x per run).
# usage: scripts/summary.sh <run dir>   (the dir holding <account>.log from the skills' runner command)
# Per account: OK/SKIP counts, every FAIL/MANUAL/paid line, the last LEFT FOR HELPER, exit state if it stopped early.
for f in "$1"/*.log; do
  a=$(basename "$f" .log)
  awk -v a="$a" '
    /^OK /   { ok++ } /^SKIP / { skip++ }
    /^(FAIL|MANUAL) |gems|PAID|Traceback/ { keep[++n] = $0 }
    /^LEFT FOR HELPER:/ { left = $0 }
    END {
      printf "== %s: %d OK, %d SKIP%s\n", a, ok, skip, left ? "" : " (no LEFT line: still running or crashed)"
      for (i = 1; i <= n; i++) print "  " substr(keep[i], 1, 200)
      if (left) print "  " left
    }' "$f"
done
