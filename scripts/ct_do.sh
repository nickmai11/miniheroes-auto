#!/bin/bash
# Crystal Throne fan-out: run the same tap.py args on every account of a group in parallel, one "<name>: <result>" line each.
# usage: scripts/ct_do.sh <g1|g2|g3|all|name[,name...]> [tap.py args...]     e.g. scripts/ct_do.sh g1 900,260 --until-text 'Main Base'
# CT_TOOL=ct_tap.py runs scripts/ct_tap.py (OCR text taps) instead of tap.py. Serials: $CT_SERIALS (default /tmp/ct_serials.txt), lines "<group> <account> <serial>". Logs every call to logs/<account>/<game day>.log.
HERE="$(cd "$(dirname "$0")" && pwd)"; TAP="$HERE/tap.py"; F=${CT_SERIALS:-/tmp/ct_serials.txt}
who=$1; shift; GD=$(TZ=UTC date -v-5H +%F)
case "$who" in all) sel=$(cat "$F");; g[0-9]) sel=$(awk -v g="$who" '$1==g' "$F");; *) sel=$(awk -v l=",$who," 'index(l,","$2",")' "$F");; esac
[ -n "$sel" ] || { echo "no accounts for '$who'"; exit 1; }
echo "$sel" | while read g n s; do
  ( if [ -n "$CT_TOOL" ]; then r=$(D=$s python3 "$HERE/$CT_TOOL" "$@" 2>&1); else r=$(D=$s python3 "$TAP" -o /tmp/ct_$n.png -w 270 "$@" 2>&1 | tail -1); fi
    echo "$n: $r"
    echo "$(date '+%F %T') [coord] ct_do $who: tap.py $* -> ${r:0:160}" >> "$HERE/../logs/$n/$GD.log" ) &
done; wait
