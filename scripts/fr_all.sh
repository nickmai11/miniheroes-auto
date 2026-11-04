#!/bin/bash
# "fr all" with no LLM (Nick, 2026-11-03: scheduler at 4:30 AM): boot every accounts/*.yaml instance, realm.py on each
# "ready" one in parallel, one result line per account. Outside a battle round it exits before booting anything.
# launchd: ~/Library/LaunchAgents/com.nickm.miniheroes-fr.plist, Wed/Thu/Fri 04:30 local (+07) = Tue/Wed/Thu 21:30 UTC,
# 30 min before the round ends; output -> logs/launchd-fr.log, per-account lines -> logs/<account>/<game day>.log.
# The plist runs it under `caffeinate -i -s` (idle sleep is 1 min: after a scheduled wake the Mac slept mid-boot risk).
# Needs AC power + lid open (or an external display): a closed lid sleeps regardless.
#   reload after plist edits: launchctl bootout gui/$(id -u)/com.nickm.miniheroes-fr; launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.nickm.miniheroes-fr.plist
# A STOP / boot failure is left for Nick (nobody to finish it at 4:30): "<account> exit 1" line + v_realm.png in /tmp/miniheroes-fr/<account>.
HERE="$(cd "$(dirname "$0")" && pwd)"; R="$(dirname "$HERE")"; W=/tmp/miniheroes-fr
echo "=== $(date)"
(cd "$HERE" && D= python3 -c 'import realm, sys; sys.exit(not realm.battle_on())') || { echo 'no battle round now'; exit 0; }
# "<index>|<account>|<instance name>" per accounts/*.yaml mumu_instance (the template's "Example" has no instance)
pairs=$(python3 - "$R" <<'EOF'
import glob, json, re, subprocess, sys
info = json.loads(subprocess.check_output(['/Applications/MuMuPlayer Pro.app/Contents/MacOS/mumu-cli', 'info', 'all']))
idx = {r['name']: r['index'] for r in info['return']['results']}
for f in sorted(glob.glob(sys.argv[1] + '/accounts/*.yaml')):
    m = re.search(r'mumu_instance:\s*(.+)', open(f).read())
    if m and m[1].strip() in idx: print(f"{idx[m[1].strip()]}|{f.rsplit('/', 1)[1][:-5]}|{m[1].strip()}")
EOF
)
# one boot.sh per index: a multi-index boot.sh ends with layout.js (osascript window tiling), pointless unattended
boot=$(for i in $(cut -d'|' -f1 <<<"$pairs"); do "$HERE/boot.sh" "$i" & done; wait)
echo "$boot"
while IFS='|' read -r i a name; do
  line=$(grep "^$name 127\.0\.0\.1:" <<<"$boot")
  case $line in
    *" ready "*) ;;
    *) echo "$a SKIPPED (${line:-no boot line})"
       echo "$(date '+%F %T') [fr_all] realm skipped: boot ${line:-no boot line}" >> "$R/logs/$a/$(TZ=UTC date -v-5H +%F).log"
       continue;;
  esac
  mkdir -p "$W/$a"
  (cd "$W/$a" && D=$(grep -o '127\.0\.0\.1:[0-9]*' <<<"$line") python3 "$HERE/realm.py" "$a" > out.txt 2>&1
   echo "$a exit $? ($(tail -1 out.txt))") &
done <<<"$pairs"
wait
echo "=== done $(date)"
