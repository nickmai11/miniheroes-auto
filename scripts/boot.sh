#!/bin/bash
# Start MuMu instances, (re)launch the game, tap Start, wait for the main screen — all in parallel.
# usage: scripts/boot.sh <mumu index>...      e.g. scripts/boot.sh 1 2 4
# prints one line per instance: "<name> 127.0.0.1:<port> ready" (or "... start-timeout" / "... main-timeout").
# With >1 instance it then runs scripts/layout.js (window tiling).
# Then scripts/stabilize.py closes the event popups; "ready (stable …)" = bare main screen, "popup-stuck" = close it by hand.
# Timings measured on Aminor 2026-10-27: Start button shows <1 s after launch, main screen ~5 s after Start.
M="/Applications/MuMuPlayer Pro.app/Contents/MacOS/mumu-cli"
HERE="$(cd "$(dirname "$0")" && pwd)"; TAP="$HERE/tap.py"
PKG=com.and.brawlen.web

boot() {
  local i=$1 port name s
  "$M" open "$i" >/dev/null 2>&1
  until port=$("$M" info "$i" 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin)['return'].get('adb_port') or '')" 2>/dev/null) && [ -n "$port" ]; do sleep 1; done
  name=$("$M" info "$i" | python3 -c "import json,sys; print(json.load(sys.stdin)['return']['name'])")
  s=127.0.0.1:$port
  # re-connect every pass: the connection can drop while booting (xFaktor 2026-10-28 hung 5 min here)
  local t=0
  until adb connect "$s" >/dev/null 2>&1; adb -s "$s" shell getprop sys.boot_completed 2>/dev/null | grep -q 1; do
    sleep 1; t=$((t+1)); [ $t -ge 90 ] && { echo "$name $s boot-timeout"; return; }
  done
  adb -s "$s" shell am force-stop $PKG
  adb -s "$s" shell monkey -p $PKG -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1
  # yellow Start button, then the blue Recruit icon of the bottom bar (dimmed while a popup is open -> still ok after timeout)
  D=$s python3 "$TAP" -o "/tmp/boot_$port.png" --until 440,1508,255,182,16 --timeout 90 || { echo "$name $s start-timeout"; return; }
  # Start tap is sometimes ignored (xFaktor/Cmajor 2026-10-27) -> re-tap up to 3x, but ONLY while the Start
  # button is still there: a blind re-tap hit an event popup's GO and opened a web page (Bino/Dino 2026-10-27).
  for try in 1 2 3; do
    D=$s python3 "$TAP" 540,1508 -o "/tmp/boot_$port.png" --until 92,1788,0,158,230 --timeout 20 && break
    D=$s python3 "$TAP" -o "/tmp/boot_$port.png" --until 440,1508,255,182,16 --timeout 1 || break  # Start gone: popup over main
    [ $try = 3 ] && { echo "$name $s main-timeout"; return; }
  done
  # clear start-up event popups (tick "Do not remind me today" + X) -> "stable" = bare main screen (Nick, 2026-10-28)
  local st; st=$(cd /tmp && D=$s python3 "$HERE/stabilize.py" | tail -1)
  case $st in stable*) echo "$name $s ready ($st)";; *) echo "$name $s popup-stuck ($st, /tmp/v_stabilize.png)";; esac
}

for i in "$@"; do boot "$i" & done
wait
# multi-account runs: tile the windows (Nick, 2026-10-27)
if [ $# -gt 1 ]; then ONLY="$*" osascript -l JavaScript "$(dirname "$0")/layout.js"; fi
