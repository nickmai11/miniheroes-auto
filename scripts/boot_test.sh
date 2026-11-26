#!/bin/bash
# Offline test of boot.sh (Nick 2026-11-22: "ensure quality for boot"): runs boot.sh against a fake emulator (stub adb /
# mumu-cli / tap.py / stabilize.py / boot_state.py) in a temp dir, ~10 s, no instance touched. The pre-commit hook runs it
# when a boot file changes. usage: scripts/boot_test.sh [boot.sh to test]   exit 0 = every scenario passed
HERE="$(cd "$(dirname "$0")" && pwd)"; SRC=${1:-$HERE/boot.sh}
python3 "$HERE/boot_state.py" --test >/dev/null || { echo "FAIL boot_state.py --test"; exit 1; }
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT; mkdir -p "$T/bin"; cp "$SRC" "$T/boot.sh"; chmod +x "$T/boot.sh"
st() { cat "$T/st/$1" 2>/dev/null || echo 0; }                      # fake device state, one file per key
cat > "$T/accounts.py" <<S
#!/bin/bash
[ "\$1" = boot-order ] && { shift; echo "\$@"; exit; }
echo "$T/mumu"
S
cat > "$T/mumu" <<S
#!/bin/bash
cd "$T/st"; case \$1 in
  close) echo 0 > connected; echo 0 > launched; echo \$((\$(cat restarts 2>/dev/null || echo 0)+1)) > restarts;;
  info) echo '{"return":{"adb_port":26999,"name":"Test"}}';;
esac; exit 0
S
cat > "$T/bin/adb" <<S
#!/bin/bash
cd "$T/st"; c=\$(cat connected 2>/dev/null || echo 0)
[ "\$1" = connect ] && { [ "\$SCEN" = nolink ] || echo 1 > connected; exit 0; }
[ "\$1" = -s ] && shift 2
[ "\$c" = 1 ] || { echo "adb: device '127.0.0.1:26999' not found" >&2; exit 1; }
case "\$*" in
  get-state) echo device;;
  *getprop*) n=\$(cat slow 2>/dev/null || echo 0); [ "\$n" -gt 0 ] && { echo \$((n-1)) > slow; echo 0; } || echo 1;;
  *force-stop*) echo 0 > launched; [ "\$SCEN" = drop ] && echo 0 > connected;;   # drop = link lost on every force-stop
  *monkey*) [ "\$SCEN" = nolaunch ] || echo 1 > launched;;
  *dumpsys*) [ "\$(cat launched 2>/dev/null)" = 1 ] && echo "mCurrentFocus=Window{x u0 com.and.brawlen.web/AppActivity}" || echo "mCurrentFocus=Window{x u0 Launcher}";;
esac; exit 0
S
cat > "$T/tap.py" <<S
import os, sys
st = lambda k: open(f'$T/st/{k}').read().strip() if os.path.exists(f'$T/st/{k}') else '0'
if st('connected') != '1': raise RuntimeError('screencap failed 3x')
if '540,1508' in sys.argv and os.environ['SCEN'] == 'dropstart' and st('dropped') != '1':   # link lost on the Start tap, once
    open('$T/st/connected', 'w').write('0'); open('$T/st/dropped', 'w').write('1'); sys.exit(1)
if '440,1508,255,182,16' in sys.argv: sys.exit(0 if st('launched') == '1' and os.environ['SCEN'] != 'logout' else 1)
S
cat > "$T/stabilize.py" <<S
if open('$T/st/connected').read().strip() != '1': raise RuntimeError('screencap failed 3x')
print('stable (0 popups closed)')
S
cat > "$T/boot_state.py" <<S
import os, subprocess
g = subprocess.run(['adb', '-s', os.environ['D'], 'get-state'], capture_output=True, text=True).stdout.strip()
print('adb-lost' if g != 'device' else 'logged-out (Log In | Password)' if os.environ['SCEN'] == 'logout' else 'other (loading)')
S
printf '#!/bin/bash\necho "CPU usage: 1%% user, 1%% sys, 98%% idle"\n' > "$T/bin/top"; chmod +x "$T"/bin/* "$T/mumu" "$T/accounts.py"
fails=0
run() {   # <scenario> <expected line regex> <expected relaunches> <expected instance restarts> [slow getprops]
  rm -rf "$T/st"; mkdir "$T/st"; echo "${5:-0}" > "$T/st/slow"
  out=$(cd "$T" && SCEN=$1 NOLAYOUT=1 PATH="$T/bin:$PATH" perl -e 'alarm 120; exec @ARGV' ./boot.sh 0 2>"$T/err"); rel=$(grep -c 'relaunch' "$T/err"); rs=$(st restarts)
  if [[ $out =~ $2 ]] && [ "$rel" = "$3" ] && [ "$rs" = "$4" ]; then echo "ok   $1: $out (relaunches $rel, restarts $rs)"
  else echo "FAIL $1: got '$out' relaunches $rel restarts $rs; want /$2/ $3 $4"; fails=$((fails+1)); fi
}
run cold     '^Test 127.0.0.1:26999 ready \(stable'  0 0     # f475aaa: a clean cold boot must be ready, not boot-timeout
run slow     '^Test 127.0.0.1:26999 ready \(stable'  0 0 3   # Android up after 3 s
run drop     '^Test 127.0.0.1:26999 ready \(stable'  0 0     # link lost at each force-stop -> reconnect (Gambler 11-22)
run dropstart '^Test 127.0.0.1:26999 ready \(stable'  0 0     # link lost on the Start tap -> reconnect, no relaunch (live 11-22)
run logout   '^Test 127.0.0.1:26999 logged-out'      0 0     # login screen -> skip at once, no relaunch (Kong 11-22)
run nolaunch '^Test 127.0.0.1:26999 start-timeout'   10 5    # game never starts -> 10 relaunches, instance restart every 2nd
# reload after "Network issue" (flow.after_restart): popups cleared like boot the moment one shows (Bino 11-22 waited ~3 min)
D=x python3 - "$HERE" <<'PY' || fails=$((fails+1))
import sys, time; sys.path.insert(0, sys.argv[1]); import flow, stabilize
def case(name, screens, want_taps, max_polls):
    seq, taps, cleared = list(screens), [], []
    cur = lambda: seq[0] if len(seq) == 1 else seq.pop(0)
    flow.grab = lambda: cur(); flow.is_main = lambda im=None: im == 'main'
    stabilize.close_x = lambda im: (980, 150) if im == 'popup' else None
    flow.ocr = lambda im=None, net=False: ([(400, 1500, 100, 40, 'Start')] if im == 'title' else
                                           [(100, 900, 300, 30, 'Do not remind me today')] if im == 'popup2' else [])
    flow.tap_wait = lambda x, y: taps.append((x, y)); time.sleep = lambda s: None
    stabilize.main = lambda: cleared.append(len(screens) - len(seq)) or 0
    ok = flow.after_restart() and cleared and cleared[0] <= max_polls and len(taps) == want_taps
    print(('ok   ' if ok else 'FAIL ') + f'reload {name}: popups cleared after {cleared[0] if cleared else None} polls, taps {taps}')
    return ok
r = [case('popup (X)', ['loading', 'loading', 'popup', 'main'], 0, 3),
     case('popup (tick text)', ['loading', 'popup2', 'main'], 0, 2),
     case('title then popup', ['title', 'loading', 'popup', 'main'], 1, 3),
     case('straight to main', ['main'], 0, 1)]
sys.exit(0 if all(r) else 1)
PY
[ $fails = 0 ] && echo "boot_test: all passed" || { echo "boot_test: $fails FAILED"; exit 1; }
