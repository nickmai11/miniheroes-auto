#!/bin/bash
# Test "scheduled wake 30 s before a launchd job" without touching the game (Nick, 2026-11-03).
# usage (Terminal, asks for your password):  scripts/test_wake.sh [HH:MM]     default = 3 min from now
#   -> wake at HH:MM-30s (pmset), a temp LaunchAgent fires at HH:MM and logs to logs/test-wake.log; then sleep the Mac
#      (Apple menu > Sleep, lid open, on the charger) and don't touch it until a few minutes after HH:MM.
#   scripts/test_wake.sh --check    show the log + remove the temp agent
LOG="$(cd "$(dirname "$0")/.." && pwd)/logs/test-wake.log"
LABEL=com.nickm.miniheroes-waketest; P=~/Library/LaunchAgents/$LABEL.plist
if [ "$1" = --check ]; then
  cat "$LOG" 2>/dev/null || echo "no log: the job never ran (Mac didn't wake, or slept before HH:MM)"
  launchctl bootout gui/$(id -u)/$LABEL 2>/dev/null; rm -f "$P"; echo "temp agent removed"; exit
fi
T=${1:-$(date -v+3M '+%H:%M')}; H=${T%%:*}; M=${T##*:}
WAKE=$(date -j -v-30S -f '%H:%M:%S' "$T:00" '+%H:%M:%S'); DAY=$(date '+%m/%d/%Y')
cat > "$P" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key><array><string>/usr/bin/caffeinate</string><string>-i</string><string>-s</string>
    <string>/bin/sh</string><string>-c</string>
    <string>echo "job fired \$(date '+%T') (scheduled $T, wake $WAKE)" >> "$LOG"; sleep 60; echo "still awake \$(date '+%T') after 60 s under caffeinate" >> "$LOG"</string></array>
  <key>StartCalendarInterval</key><dict><key>Hour</key><integer>$((10#$H))</integer><key>Minute</key><integer>$((10#$M))</integer></dict>
</dict></plist>
EOF
launchctl bootout gui/$(id -u)/$LABEL 2>/dev/null; launchctl bootstrap gui/$(id -u) "$P" || exit 1
rm -f "$LOG"
sudo pmset schedule wake "$DAY $WAKE" || exit 1
pmset -g sched | grep "$WAKE"
echo "set: wake $WAKE, job $T. Sleep the Mac now; after $T + 2 min run: scripts/test_wake.sh --check"
