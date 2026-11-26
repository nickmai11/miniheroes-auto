#!/bin/bash
# Give the Mac back the disk space Android freed inside MuMu instances (data.qcow2 only grows: every game update
# allocates new blocks and deleted files are never returned) - `fstrim /data` as root, ~5 s (tested on Cino 2026-11-26:
# 7.9G -> 5.2G, qemu-img check clean). Frees space, deletes nothing.
# usage: scripts/trim.sh <mumu index>...    one at a time; prints "<index> <name> <before> -> <after> GB"
#   running instance: trimmed in place, left running - never while a task runs on it (caller's job).
#   stopped instance: opened (Android only, no game), trimmed, closed again - left open if the game was started
#   meanwhile (somebody else booted it).
M="$("$(dirname "$0")/accounts.py" mumu)"; PKG=com.and.brawlen.web
get() { "$M" info "$1" 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin)['return'].get('$2') or '')" 2>/dev/null; }
gb() { du -k "$1" | awk '{printf "%.1f", $1/1048576}'; }
for i in "$@"; do
  img="$(get "$i" bundle_path)/data.qcow2"; name=$(get "$i" name); was=$(get "$i" state); before=$(gb "$img")
  [ -f "$img" ] || { echo "$i FAIL no data.qcow2"; continue; }
  if [ "$was" = stopped ]; then "$M" open "$i" >/dev/null 2>&1; fi
  s=; for _ in $(seq 60); do   # ~2 min for Android to come up
    p=$(get "$i" adb_port); s=127.0.0.1:$p
    [ -n "$p" ] && adb connect "$s" >/dev/null 2>&1 && [ "$(adb -s "$s" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" = 1 ] && break
    s=; sleep 2
  done
  [ -n "$s" ] || { echo "$i $name FAIL Android not up (state $(get "$i" state)) - left as is"; continue; }
  out=$("$M" control "$i" --action run_cmd --cmd "fstrim -v /data" 2>&1 | grep -o '[0-9]* bytes trimmed')
  if [ "$was" = stopped ]; then
    if adb -s "$s" shell pidof $PKG 2>/dev/null | grep -q .; then note=" (game running - left open)"
    else "$M" close "$i" >/dev/null 2>&1; until [ "$(get "$i" state)" = stopped ]; do sleep 1; done; note=; fi
  else note=" (running - left open)"; fi
  echo "$i $name $before -> $(gb "$img") GB${out:+, }${out:-, FAIL no trim output}$note"
done
