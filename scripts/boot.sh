#!/bin/bash
# Start MuMu instances, (re)launch the game, tap Start, wait for the main screen — all in parallel.
# usage: [NOLAYOUT=1] scripts/boot.sh <mumu index>...      e.g. scripts/boot.sh 1 2 4
# prints one line per instance: "<name> 127.0.0.1:<port> ready" (or "... start-timeout (<why>)" / "... main-timeout" /
# "... logged-out (<screen>)" = login screen, no relaunch, skip the account). Test: scripts/boot_test.sh (pre-commit runs it).
# Then it runs scripts/layout.js (window tiling, layout 1 - every task, Nick 2026-11-19), unless NOLAYOUT=1 (stage climb only: Nick 2026-11-14).
# Then scripts/stabilize.py closes the event popups; "ready (stable …)" = bare main screen, "popup-stuck" = close it by hand.
# Timings measured on Aminor 2026-10-27: Start button shows <1 s after launch, main screen ~5 s after Start.
HERE="$(cd "$(dirname "$0")" && pwd)"; TAP="$HERE/tap.py"
M=$("$HERE/accounts.py" mumu)   # mumu-cli path: one copy, accounts.py
# boot order = the windows right to left, top to bottom (Nick 2026-11-22); lookup failed -> as given
o=$("$HERE/accounts.py" boot-order "$@" 2>/dev/null) && [ -n "$o" ] && set -- $o
# the game: web build on Kong, store build on the instances cloned from "Android Device" (reset 2026-11-27)
PKGS="com.and.brawlen.web com.and.brawl.en"

# the ONE relaunch limit (Nick 2026-11-20, every task): game dead after a launch -> launch again, up to this many
# times; flow.relaunch() (mission scripts, runner home()) reads it from here as its per-run cap.
MAX_RELAUNCHES=10
in_game() { adb -s "$1" shell dumpsys window 2>/dev/null | grep mCurrentFocus | grep -q AppActivity; }

game() {   # <serial> <instance name> <port>: force-stop, launch, Start, popups -> one status line
  local s=$1 name=$2 port=$3 why=
  # the ADB link can drop any time (Gambler, Boudior 2026-11-22: 'device not found' through 10 relaunches, one manual
  # `adb connect` fixed it) -> reconnect before every adb step of a launch, not only in up()
  adb connect "$s" >/dev/null 2>&1; for p in $PKGS; do adb -s "$s" shell am force-stop $p; done
  # yellow Start button, then the blue Recruit icon of the bottom bar (dimmed while a popup is open -> still ok after timeout)
  # launch can silently not happen (Aminor 2026-11-03 sat on the Android home 90 s) -> relaunch every 30 s, 3 tries
  local ok=
  for try in 1 2 3; do
    adb connect "$s" >/dev/null 2>&1
    for p in $PKGS; do adb -s "$s" shell monkey -p $p -c android.intent.category.LAUNCHER 1 >/dev/null 2>&1; done
    D=$s python3 "$TAP" -o "/tmp/boot_$port.png" --until 440,1508,255,182,16 --timeout 30 2>/dev/null && { ok=1; break; }
    # why no Start: adb-lost / not-in-front -> next try reconnects + relaunches; logged-out -> stop now (Nick 2026-11-22:
    # skip that account for the task, never log it in); the screen stays as it is for Nick
    why=$(D=$s python3 "$HERE/boot_state.py" 2>&1 | tail -1)
    [[ $why == logged-out* ]] && { echo "$why"; return; }
  done
  [ -n "$ok" ] || { echo "start-timeout (${why:0:80})"; return; }
  # Start tap is sometimes ignored (pawn1/Cmajor 2026-10-27) -> re-tap up to 3x, but ONLY while the Start
  # button is still there: a blind re-tap hit an event popup's GO and opened a web page (Bino/Dino 2026-10-27).
  for try in 1 2 3; do
    adb connect "$s" >/dev/null 2>&1   # link drops after Start too (live test 2026-11-22: cost a whole relaunch)
    D=$s python3 "$TAP" 540,1508 -o "/tmp/boot_$port.png" --until 92,1788,0,158,230 --timeout 20 && break
    D=$s python3 "$TAP" -o "/tmp/boot_$port.png" --until 440,1508,255,182,16 --timeout 1 || break  # Start gone: popup over main
    [ $try = 3 ] && { echo main-timeout; return; }
  done
  # clear start-up event popups (tick "Do not remind me today" + X) -> "stable" = bare main screen (Nick, 2026-10-28)
  adb connect "$s" >/dev/null 2>&1
  local st; st=$(cd /tmp && D=$s NAME="$name" python3 "$HERE/stabilize.py" | tail -1)
  case $st in stable*) echo "ready ($st)";; *) echo "popup-stuck ($st, /tmp/v_stabilize.png)";; esac
}

up() {   # <index>: open the instance, wait for Android -> sets port name s; 1 = boot-timeout
  "$M" open "$1" >/dev/null 2>&1
  until port=$("$M" info "$1" 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin)['return'].get('adb_port') or '')" 2>/dev/null) && [ -n "$port" ]; do sleep 1; done
  # info can fail for a moment ("Error: invalidPort", pawn2 2026-11-17 printed with no name) -> retry
  until name=$("$M" info "$1" 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin)['return']['name'])" 2>/dev/null) && [ -n "$name" ]; do sleep 1; done
  s=127.0.0.1:$port
  # re-connect every pass: the connection can drop while booting (pawn1 2026-10-28 hung 5 min here)
  local t=0 g
  until adb connect "$s" >/dev/null 2>&1; g=$(adb -s "$s" shell getprop sys.boot_completed 2>&1); grep -q 1 <<<"$g"; do
    sleep 1; t=$((t+1)); [ $t -ge 90 ] && { echo "$name $s Android not up after 90 s (getprop: ${g:-empty})" >&2; return 1; }
  done
  return 0   # not the loop's status: the last body command ([ t -ge 90 ] false) made every cold boot a "timeout" (11-21 catch-ups)
}

boot() {
  local i=$1 port name s
  # tasks run at 30 fps, every instance incl. Kong/Cmajor; back to 60 when the task is done (Nick 2026-11-13).
  # The fps cap applies live (< 30 is ignored); 1 core = default, applies at instance start (Nick 2026-11-17).
  "$M" config "$i" --setting '{"maxFpsLimit":30,"vmCpuCount":1}' >/dev/null 2>&1
  # never give up on an instance (Nick 2026-11-21): Android not up -> close + open it again, max MAX_RELAUNCHES
  local r
  for r in $(seq $MAX_RELAUNCHES); do
    up "$i" && break
    [ $r = $MAX_RELAUNCHES ] && { echo "$name $s boot-timeout"; return; }
    echo "$name $s restarting the instance (boot $r/$MAX_RELAUNCHES)" >&2; "$M" close "$i" >/dev/null 2>&1
  done
  # game dead after a launch (Android home in front: Boudior, Kratos 11-19) -> launch again, max MAX_RELAUNCHES
  local n st
  for n in $(seq $MAX_RELAUNCHES); do
    st=$(game "$s" "$name" "$port")
    [[ $st == ready* || $st == logged-out* ]] || in_game "$s" && break
    echo "$name $s $st, game not in front -> relaunch $n/$MAX_RELAUNCHES" >&2
    # whatever it takes (Nick 2026-11-21): the game never starting (Gambler 11-21: launch sent, no activity, 4 relaunches)
    # needs the instance itself restarted -> every 2nd failed relaunch: close + open the instance
    if [ $((n % 2)) = 0 ]; then
      echo "$name $s restarting the instance" >&2
      "$M" close "$i" >/dev/null 2>&1; up "$i" || echo "$name $s instance restart: Android not up, next relaunch retries" >&2
    fi
  done
  echo "$name $s $st"
}

# every instance at once, no batches (Nick 2026-11-27: "remove rule to boot batch, just boot all")
for i in "$@"; do boot "$i" & done; wait
# tile the windows (Nick 2026-10-27), a single re-boot too: it goes back to its slot (Nick 2026-11-19)
if [ -z "$NOLAYOUT" ]; then ONLY="$*" osascript -l JavaScript "$(dirname "$0")/layout.js"; fi
