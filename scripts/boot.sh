#!/bin/bash
# Start MuMu instances, (re)launch the game, tap Start, wait for the main screen — all in parallel.
# usage: [NOLAYOUT=1] scripts/boot.sh <mumu index>...      e.g. scripts/boot.sh 1 2 4  (>4: in batches of 4, see below)
# prints one line per instance: "<name> 127.0.0.1:<port> ready" (or "... start-timeout" / "... main-timeout").
# Then it runs scripts/layout.js (window tiling, layout 1 - every task, Nick 2026-11-19), unless NOLAYOUT=1 (stage climb only: Nick 2026-11-14).
# Then scripts/stabilize.py closes the event popups; "ready (stable …)" = bare main screen, "popup-stuck" = close it by hand.
# Timings measured on Aminor 2026-10-27: Start button shows <1 s after launch, main screen ~5 s after Start.
M="/Applications/MuMuPlayer Pro.app/Contents/MacOS/mumu-cli"
HERE="$(cd "$(dirname "$0")" && pwd)"; TAP="$HERE/tap.py"
PKG=com.and.brawlen.web

# the ONE relaunch limit (Nick 2026-11-20, every task): game dead after a launch -> launch again, up to this many
# times; flow.relaunch() (mission scripts, runner home()) reads it from here as its per-run cap.
MAX_RELAUNCHES=10
in_game() { adb -s "$1" shell dumpsys window 2>/dev/null | grep mCurrentFocus | grep -q AppActivity; }

game() {   # <serial> <instance name> <port>: force-stop, launch, Start, popups -> one status line
  local s=$1 name=$2 port=$3
  adb -s "$s" shell am force-stop $PKG
  # yellow Start button, then the blue Recruit icon of the bottom bar (dimmed while a popup is open -> still ok after timeout)
  # launch can silently not happen (Aminor 2026-11-03 sat on the Android home 90 s) -> relaunch every 30 s, 3 tries
  local ok=
  for try in 1 2 3; do
    adb -s "$s" shell monkey -p $PKG -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1
    D=$s python3 "$TAP" -o "/tmp/boot_$port.png" --until 440,1508,255,182,16 --timeout 30 && { ok=1; break; }
  done
  [ -n "$ok" ] || { echo start-timeout; return; }
  # Start tap is sometimes ignored (xFaktor/Cmajor 2026-10-27) -> re-tap up to 3x, but ONLY while the Start
  # button is still there: a blind re-tap hit an event popup's GO and opened a web page (Bino/Dino 2026-10-27).
  for try in 1 2 3; do
    D=$s python3 "$TAP" 540,1508 -o "/tmp/boot_$port.png" --until 92,1788,0,158,230 --timeout 20 && break
    D=$s python3 "$TAP" -o "/tmp/boot_$port.png" --until 440,1508,255,182,16 --timeout 1 || break  # Start gone: popup over main
    [ $try = 3 ] && { echo main-timeout; return; }
  done
  # clear start-up event popups (tick "Do not remind me today" + X) -> "stable" = bare main screen (Nick, 2026-10-28)
  local st; st=$(cd /tmp && D=$s NAME="$name" python3 "$HERE/stabilize.py" | tail -1)
  case $st in stable*) echo "ready ($st)";; *) echo "popup-stuck ($st, /tmp/v_stabilize.png)";; esac
}

boot() {
  local i=$1 port name s
  # tasks run at 30 fps, every instance incl. Kong/Cmajor; back to 60 when the task is done (Nick 2026-11-13).
  # The fps cap applies live (< 30 is ignored); 1 core = default, applies at instance start (Nick 2026-11-17).
  "$M" config "$i" --setting '{"maxFpsLimit":30,"vmCpuCount":1}' >/dev/null 2>&1
  "$M" open "$i" >/dev/null 2>&1
  until port=$("$M" info "$i" 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin)['return'].get('adb_port') or '')" 2>/dev/null) && [ -n "$port" ]; do sleep 1; done
  # info can fail for a moment ("Error: invalidPort", fGotten 2026-11-17 printed with no name) -> retry
  until name=$("$M" info "$i" 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin)['return']['name'])" 2>/dev/null) && [ -n "$name" ]; do sleep 1; done
  s=127.0.0.1:$port
  # re-connect every pass: the connection can drop while booting (xFaktor 2026-10-28 hung 5 min here)
  local t=0
  until adb connect "$s" >/dev/null 2>&1; adb -s "$s" shell getprop sys.boot_completed 2>/dev/null | grep -q 1; do
    sleep 1; t=$((t+1)); [ $t -ge 90 ] && { echo "$name $s boot-timeout"; return; }
  done
  # game dead after a launch (Android home in front: Boudior, Kratos 11-19) -> launch again, max MAX_RELAUNCHES
  local n st
  for n in $(seq $MAX_RELAUNCHES); do
    st=$(game "$s" "$name" "$port")
    [[ $st == ready* ]] || in_game "$s" || { echo "$name $s $st, game not in front -> relaunch $n/$MAX_RELAUNCHES" >&2; continue; }
    break
  done
  echo "$name $s $st"
}

idle() { top -l 2 -s 1 | awk '/CPU usage/{v=$7} END{print int(v)}'; }
# at most 4 boots at once, the next 4 once the CPU has calmed down - 11 boots at once pegged the CPU (Nick 2026-11-17,
# every task). Calm = idle >= 70%, or back near the idle before the 1st batch when other instances already load it; max ~2 min.
want=$(idle); want=$(( want - 10 < 70 ? want - 10 : 70 ))
for ((k=0; k<$#; k+=4)); do
  [ $k -gt 0 ] && for t in $(seq 60); do [ "$(idle)" -ge "$want" ] && break; done
  for i in "${@:k+1:4}"; do boot "$i" & done; wait
done
# tile the windows (Nick 2026-10-27), a single re-boot too: it goes back to its slot (Nick 2026-11-19)
if [ -z "$NOLAYOUT" ]; then ONLY="$*" osascript -l JavaScript "$(dirname "$0")/layout.js"; fi
