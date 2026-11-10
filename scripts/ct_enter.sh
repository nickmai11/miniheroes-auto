#!/bin/bash
# Crystal Throne: put each instance on the battlefield (main → Tribe → scroll down → Crystal Throne card → Enter), all in parallel.
# usage: scripts/ct_enter.sh <serial>...   prints "<serial> on-battlefield" or "<serial> FAIL <step>" (screenshot /tmp/ct_<port>.png)
HERE="$(cd "$(dirname "$0")" && pwd)"; TAP="$HERE/tap.py"
one() {
  local s=$1 p=${1##*:} o=/tmp/ct_$p.png
  D=$s python3 "$TAP" 448,1780 -o $o --until-text 'Canyon Clash|Poseidon' --timeout 10 >/dev/null || { echo "$s FAIL tribe"; return; }
  adb -s $s shell input swipe 540 1500 540 600 400; sleep 0.8
  D=$s python3 "$TAP" 540,1540 -o $o --until-text 'Start in|^Enter$|Selection|Participation' --timeout 10 >/dev/null || { echo "$s FAIL card"; return; }
  D=$s python3 "$TAP" 540,1478 -o $o --until-text 'Battle Report|Contribution' --timeout 15 >/dev/null || { echo "$s FAIL enter"; return; }
  echo "$s on-battlefield"
}
for s in "$@"; do one "$s" & done; wait
