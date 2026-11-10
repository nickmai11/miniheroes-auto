#!/bin/bash
# Crystal Throne free-revive watcher (Nick, 2026-11-08: free revives whenever available). Every ~1-2 s per account:
# "Tap anywhere to close" defeat result -> close it; "Severely injured" popup -> tap Free Revive (760,1263; Revive Now =
# scroll, left button, never tapped) every ~1 s through its 60 s cooldown until it takes, stop at free Times 0/5;
# Defeated with the popup closed -> big Revive button (840,1600) reopens it. Exits when no account is on the battlefield any more (match over) or after $1 min.
HERE="$(cd "$(dirname "$0")" && pwd)"; TAP="$HERE/tap.py"; F=${CT_SERIALS:-/tmp/ct_serials.txt}; GD=$(TZ=UTC date -v-5H +%F)
end=$(( $(date +%s) + ${1:-45} * 60 ))
watch() { local n=$1 s=$2 t last=0
  while [ $(date +%s) -lt $end ]; do
    t=$(D=$s python3 "$TAP" -o /tmp/ctw_$n.png -w 270 --until-text . --timeout 2 2>/dev/null)
    if echo "$t" | grep -q 'Severely injured'; then
      # free count = the 2nd "Times:N/M" (1st = Revive Now scrolls); 0 left -> leave it (scrolls only on Nick's order)
      free=$(echo "$t" | grep -oE 'Times: ?[0-9]+/[0-9]+' | sed -n 2p | grep -oE '[0-9]+' | head -1)
      if [ "$free" = 0 ]; then [ $last = 0 ] && echo "$(date +%T) $n no free revives left"; last=1; sleep 5; continue; fi
      D=$s python3 "$TAP" 760,1263 -o /tmp/ctw_$n.png -w 270 >/dev/null 2>&1   # 60 s cooldown: tap every ~1 s until it takes
      t2=$(D=$s python3 "$TAP" -o /tmp/ctw_$n.png -w 270 --until-text . --timeout 2 2>/dev/null)
      if echo "$t2" | grep -q 'Severely injured'; then
        cd=$(echo "$t2" | grep -oE '[0-9]{1,2}:[0-9]{2}(:[0-9]{2})?|[0-9]+ ?s\b' | tr '\n' ' ')
        [ "$cd" != "$last" ] && echo "$(date +%T) $n free revive not ready (on screen: ${cd:-no timer read})"; last=$cd
      else echo "$(date +%T) $n revived"; last=0; echo "$(date '+%F %T') [coord] ct_revive: Free Revive -> revived" >> "$HERE/../logs/$n/$GD.log"; fi
      continue
    elif echo "$t" | grep -q 'Tap anywhere to close'; then D=$s python3 "$TAP" 540,1500 -o /tmp/ctw_$n.png -w 270 >/dev/null 2>&1; continue
    elif echo "$t" | grep -qE 'Battle ends|Rewards \| Ranking|Settlement'; then echo "$(date +%T) $n off battlefield, stop"; return
    elif echo "$t" | grep -q 'Defeated' && echo "$t" | grep -qE '(^|\| )Revive( \||$)'; then
      # popup closed (X / stray tap) but still defeated: the big Revive button (840,1600) reopens it — 11-08 Cris/PuPu/xFaktor sat here
      D=$s python3 "$TAP" 840,1600 -o /tmp/ctw_$n.png -w 270 >/dev/null 2>&1; continue; fi
    sleep 1
  done; }
while read g n s; do watch $n $s & done < "$F"; wait; echo watcher done
