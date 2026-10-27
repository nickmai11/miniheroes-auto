#!/bin/bash
# Start MuMu instances, (re)launch the game, tap Start, wait for the main screen — all in parallel.
# usage: scripts/boot.sh <mumu index>...      e.g. scripts/boot.sh 1 2 4
# prints one line per instance: "<name> 127.0.0.1:<port> ready" (or "... start-timeout" / "... main-timeout").
# Event popups may still be open on the main screen — the caller closes them.
# Timings measured on Aminor 2026-10-27: Start button shows <1 s after launch, main screen ~5 s after Start.
M="/Applications/MuMuPlayer Pro.app/Contents/MacOS/mumu-cli"
TAP="$(dirname "$0")/tap.py"
PKG=com.and.brawlen.web

boot() {
  local i=$1 port name s
  "$M" open "$i" >/dev/null 2>&1
  until port=$("$M" info "$i" 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin)['return'].get('adb_port') or '')" 2>/dev/null) && [ -n "$port" ]; do sleep 1; done
  name=$("$M" info "$i" | python3 -c "import json,sys; print(json.load(sys.stdin)['return']['name'])")
  s=127.0.0.1:$port
  adb connect "$s" >/dev/null
  until adb -s "$s" shell getprop sys.boot_completed 2>/dev/null | grep -q 1; do sleep 1; done
  adb -s "$s" shell am force-stop $PKG
  adb -s "$s" shell monkey -p $PKG -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1
  # yellow Start button, then the blue Recruit icon of the bottom bar (dimmed while a popup is open -> still ok after timeout)
  D=$s python3 "$TAP" -o "/tmp/boot_$port.png" --until 440,1508,255,182,16 --timeout 90 || { echo "$name $s start-timeout"; return; }
  D=$s python3 "$TAP" 540,1508 -o "/tmp/boot_$port.png" --until 92,1788,0,158,230 --timeout 60 || { echo "$name $s main-timeout"; return; }
  echo "$name $s ready"
}

for i in "$@"; do boot "$i" & done
wait
