#!/bin/bash
# "fr all" / "tc all" with no LLM (Nick, 2026-11-03: scheduler at 4:30 AM): boot every accounts/tasks.yaml `realm` (or `tc`)
# instance, realm.py (or tc.py) on each "ready" one in parallel, one result line per account. Outside a battle round it
# exits before booting anything. The two events alternate weekly (Nick, 2026-11-10): fr battle weeks = Tue 2026-11-03 + 14n,
# tc = the weeks between (Tue 2026-11-10 + 14n); same Tue/Wed/Thu 10:00-22:00 UTC rounds.
# launchd: ~/Library/LaunchAgents/com.nickm.miniheroes-fr.plist, Wed/Thu/Fri 04:30 local (+07) = Tue/Wed/Thu 21:30 UTC,
# 30 min before the round ends; output -> logs/launchd-fr.log, per-account lines -> logs/<account>/<game day>.log.
# The plist runs it under `caffeinate -i -s` (idle sleep is 1 min: after a scheduled wake the Mac slept mid-boot risk).
# Needs AC power + lid open (or an external display): a closed lid sleeps regardless.
# The Mac wakes itself at 04:29 Wed/Thu/Fri (pmset repeat wakepoweron, /Library/Preferences/SystemConfiguration/com.apple.AutoWake.plist
# weekdays 28), so no instance has to stay open overnight; display off / locked is fine.
# When done it closes every instance it booted (Nick 2026-11-12: computer usage).
#   reload after plist edits: launchctl bootout gui/$(id -u)/com.nickm.miniheroes-fr; launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.nickm.miniheroes-fr.plist
# A STOP / boot failure is left for Nick (nobody to finish it at 4:30): "<account> exit 1" line + v_realm.png in /tmp/miniheroes-fr/<account>.
HERE="$(cd "$(dirname "$0")" && pwd)"; R="$(dirname "$HERE")"; W=/tmp/miniheroes-fr
echo "=== $(date)"
# which event's round is on: realm (fr) or tc
ev=$(cd "$HERE" && D= python3 -c 'import datetime, realm; d = (realm.NOW.date() - datetime.date(2026, 11, 3)).days % 14
print("realm" if realm.battle_on() else "tc" if 7 <= d < 10 and 10 <= realm.NOW.hour < 22 else "")')
[ -n "$ev" ] || { echo 'no battle round now'; exit 0; }
echo "event: $ev"
# "<index>|<account>|<instance name>" per accounts/*.yaml mumu_instance (the template's "Example" has no instance)
pairs=$(python3 - "$R" "$ev" <<'EOF'
import glob, json, re, subprocess, sys
sys.path.insert(0, sys.argv[1] + '/scripts'); from accounts import for_task
want = for_task(sys.argv[2])   # accounts/tasks.yaml
info = json.loads(subprocess.check_output(['/Applications/MuMuPlayer Pro.app/Contents/MacOS/mumu-cli', 'info', 'all']))
idx = {r['name']: r['index'] for r in info['return']['results']}
for f in sorted(glob.glob(sys.argv[1] + '/accounts/*.yaml')):
    m = re.search(r'mumu_instance:\s*(.+)', open(f).read())
    if m and m[1].strip() in idx and f.rsplit('/', 1)[1][:-5] in want: print(f"{idx[m[1].strip()]}|{f.rsplit('/', 1)[1][:-5]}|{m[1].strip()}")
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
       echo "$(date '+%F %T') [fr_all] $ev skipped: boot ${line:-no boot line}" >> "$R/logs/$a/$(TZ=UTC date -v-5H +%F).log"
       continue;;
  esac
  mkdir -p "$W/$a"
  if [ "$ev" = realm ]; then cmd=("$HERE/realm.py" "$a"); else cmd=("$HERE/tc.py"); fi
  (cd "$W/$a" && D=$(grep -o '127\.0\.0\.1:[0-9]*' <<<"$line") python3 "${cmd[@]}" > out.txt 2>&1
   echo "$a exit $? ($(tail -1 out.txt))") &
done <<<"$pairs"
wait
"/Applications/MuMuPlayer Pro.app/Contents/MacOS/mumu-cli" close "$(cut -d'|' -f1 <<<"$pairs" | paste -sd, -)" >/dev/null && echo "closed instances $(cut -d'|' -f1 <<<"$pairs" | paste -sd, -)"
echo "=== done $(date)"
