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
# Kong II (S288, on Kong's instance) runs right after Kong, then the instance goes back to Kong (Nick 2026-11-17).
# A STOP / boot failure is left for Nick (nobody to finish it at 4:30): "<account> exit 1" line + v_realm.png in /tmp/miniheroes-fr/<account>.
HERE="$(cd "$(dirname "$0")" && pwd)"; R="$(dirname "$HERE")"; W=/tmp/miniheroes-fr
M=$("$HERE/accounts.py" mumu)   # mumu-cli path: one copy, accounts.py
echo "=== $(date)"
# which event's round is on: realm (fr) or tc
ev=$(cd "$HERE" && D= python3 -c 'import datetime, realm; d = (realm.NOW.date() - datetime.date(2026, 11, 3)).days % 14
print("realm" if realm.battle_on() else "tc" if 7 <= d < 10 and 10 <= realm.NOW.hour < 22 else "")')
[ -n "$ev" ] || { echo 'no battle round now'; exit 0; }
echo "event: $ev"
pairs=$("$HERE/accounts.py" rows "$ev")   # "<index>|<account>|<instance>|<port>"
boot=$("$HERE/boot.sh" $(cut -d'|' -f1 <<<"$pairs"))   # boot.sh does the halves (CPU)
echo "$boot"
run() {   # <account>: this round's script on $D, output in $W/<account>, one result line
  local cmd; mkdir -p "$W/$1"
  if [ "$ev" = realm ]; then cmd=("$HERE/realm.py" "$1"); else cmd=("$HERE/tc.py"); fi
  (cd "$W/$1" && python3 "${cmd[@]}" > out.txt 2>&1; echo "$1 exit $? ($(tail -1 out.txt))")
}
while IFS='|' read -r i a name _; do
  line=$(grep "^$name 127\.0\.0\.1:" <<<"$boot")
  case $line in
    *" ready "*) ;;
    *) echo "$a SKIPPED (${line:-no boot line})"
       echo "$(date '+%F %T') [fr_all] $ev skipped: boot ${line:-no boot line}" >> "$R/logs/$a/$("$HERE/accounts.py" game-day).log"
       continue;;
  esac
  (export D=$(grep -o '127\.0\.0\.1:[0-9]*' <<<"$line"); run "$a"
   # Kong II once Kong is done, then back to Kong (CLAUDE.md "Kong II"); stabilize.py exit 0 = that account's ID on screen
   if [ "$a" = kong ]; then
     cd "$W/kong"
     . "$HERE/kong_ii.sh"; with_kong_ii run kong_ii
   fi) &
done <<<"$pairs"
wait
"$M" close "$(cut -d'|' -f1 <<<"$pairs" | paste -sd, -)" >/dev/null && echo "closed instances $(cut -d'|' -f1 <<<"$pairs" | paste -sd, -)"
"$M" config all --setting '{"maxFpsLimit":60}' >/dev/null && echo "fps back to 60"   # boot.sh set 30 (Nick 2026-11-13)
echo "=== done $(date)"
